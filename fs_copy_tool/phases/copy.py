"""
File: fs-copy-tool/phases/copy.py
Description: Copy phase logic for Non-Redundant Media File Copy Tool
"""
import logging
import sqlite3
from pathlib import Path
from fs_copy_tool.utils.uidpath import UidPath
from fs_copy_tool.utils.fileops import copy_file, verify_file
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

def reset_status_for_missing_files(db_path, dst_roots):
    """
    For any file marked as done but missing from all destination roots, reset its status to 'pending'.
    """
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT uid, relative_path, copy_status FROM source_files
        """)
        candidates = cur.fetchall()
    for uid, rel_path, copy_status in candidates:
        missing = False
        for dst_root in dst_roots:
            dst_file = Path(dst_root) / rel_path
            if not dst_file.exists():
                missing = True
                break
        if copy_status == 'done' and missing:
            mark_copy_status(db_path, uid, rel_path, 'pending', 'Destination file missing, will retry')

def get_pending_copies(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT uid, relative_path, size, last_modified, checksum FROM source_files
            WHERE (copy_status IS NULL OR copy_status='pending' OR copy_status='error' OR copy_status='in_progress')
        """)
        return cur.fetchall()

def checksum_exists_in_destination(db_path, checksum):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM destination_files WHERE checksum=? LIMIT 1", (checksum,))
        return cur.fetchone() is not None

def mark_copy_status(db_path, uid, rel_path, status, error_message=None):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE source_files SET copy_status=?, last_copy_attempt=strftime('%s','now'), error_message=?
            WHERE uid=? AND relative_path=?
        """, (status, error_message, uid, rel_path))
        conn.commit()

def copy_files(db_path, src_roots, dst_roots, threads=4):
    import os
    uid_path = UidPath()
    reset_status_for_missing_files(db_path, dst_roots)
    pending = get_pending_copies(db_path)
    if not pending:
        return
    copied_checksums = set()
    copied_lock = Lock()
    def process_copy(args):
        uid, rel_path, size, last_modified, checksum = args
        if not checksum:
            mark_copy_status(db_path, uid, rel_path, 'error', 'No checksum')
            logging.error(f"[AGENT][COPY] Skipped (no checksum): {rel_path}")
            return False
        dst_file_exists = False
        for dst_root in dst_roots:
            dst_file = Path(dst_root) / rel_path
            if dst_file.exists():
                dst_file_exists = True
                break
        with copied_lock:
            # Only skip if both: checksum exists in DB AND file exists on disk
            if checksum_exists_in_destination(db_path, checksum) and dst_file_exists:
                mark_copy_status(db_path, uid, rel_path, 'done')
                logging.info(f"[AGENT][COPY] Skipped (already copied and file exists): {rel_path}")
                return True
            copied_checksums.add(checksum)
        src_mount = uid if os.path.isdir(uid) else uid_path.get_mount_point_from_volume_id(uid)
        if not src_mount and os.path.isdir(uid):
            src_mount = uid
        if not src_mount:
            mark_copy_status(db_path, uid, rel_path, 'error', 'Source volume not available')
            logging.error(f"[AGENT][COPY] Skipped (source volume not available): {rel_path} (uid={uid})")
            return False
        src_file = Path(src_mount) / rel_path
        for dst_root in dst_roots:
            dst_uid = dst_root if os.path.isdir(dst_root) else uid_path.get_volume_id_from_path(dst_root)
            dst_mount = dst_uid if os.path.isdir(dst_uid) else uid_path.get_mount_point_from_volume_id(dst_uid)
            if not dst_mount and os.path.isdir(dst_uid):
                dst_mount = dst_uid
            if not dst_mount:
                continue
            dst_file = Path(dst_mount) / rel_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                mark_copy_status(db_path, uid, rel_path, 'in_progress')
                def log_progress(percent, copied, total):
                    if percent % 10 == 0 or percent == 100:
                        logging.info(f"[AGENT][COPY][PROGRESS] {rel_path}: {percent}% ({copied}/{total} bytes)")
                # Always restart file copy; no chunk-level resume
                src_checksum, dst_checksum = copy_file(src_file, dst_file, progress_callback=log_progress, show_progressbar=True)
                if src_checksum == dst_checksum == checksum:
                    with sqlite3.connect(db_path) as conn:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO destination_files (uid, relative_path, size, last_modified, checksum, checksum_stale, copy_status)
                            VALUES (?, ?, ?, ?, ?, 0, 'done')
                            ON CONFLICT(uid, relative_path) DO UPDATE SET
                                size=excluded.size,
                                last_modified=excluded.last_modified,
                                checksum=excluded.checksum,
                                checksum_stale=0,
                                copy_status='done'
                        """, (dst_uid, rel_path, size, last_modified, checksum))
                        conn.commit()
                    mark_copy_status(db_path, uid, rel_path, 'done')
                    logging.info(f"Copied: {src_file} -> {dst_file}")
                else:
                    mark_copy_status(db_path, uid, rel_path, 'error', 'Verification failed')
                    logging.error(f"Verification failed: {src_file} -> {dst_file}")
            except Exception as e:
                mark_copy_status(db_path, uid, rel_path, 'error', str(e))
                logging.error(f"Copy error: {src_file} -> {dst_file}: {e}")
            break  # Only copy to one destination
        return True
    with tqdm(total=len(pending), desc="Copying files") as pbar:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(process_copy, args) for args in pending]
            for f in as_completed(futures):
                pbar.update(1)
