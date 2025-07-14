"""
File: fs-copy-tool/phases/copy.py
Description: Copy phase logic for Non-Redundant Media File Copy Tool
"""
import logging
import sqlite3
from pathlib import Path
from fs_copy_tool.utils.fileops import copy_file, verify_file
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.uidpath import UidPath
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time
import threading

def reset_status_for_missing_files(db_path, dst_roots):
    """
    For any file marked as done but missing from all destination roots, reset its status to 'pending'.
    """
    import os
    from pathlib import Path
    import sys
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT uid, relative_path, copy_status FROM source_files
        """)
        candidates = cur.fetchall()
        for uid, rel_path, copy_status in candidates:
            print(f"[DEBUG] Checking file: uid={uid}, rel_path={rel_path}, copy_status={copy_status}", file=sys.stderr)
            sys.stderr.flush()
            missing = True
            for dst_root in dst_roots:
                dst_file = Path(dst_root) / rel_path
                print(f"[DEBUG]   Checking dst_file={dst_file} exists={dst_file.exists()}", file=sys.stderr)
                sys.stderr.flush()
                if dst_file.exists():
                    missing = False
                    break
            if copy_status == 'done' and missing:
                print(f"[DEBUG] Resetting {rel_path} to pending (was done, now missing)", file=sys.stderr)
                sys.stderr.flush()
                mark_copy_status(db_path, uid, rel_path, 'pending', 'Destination file missing, will retry')
        conn.commit()  # Ensure all changes are flushed
    print(f"[DEBUG] reset_status_for_missing_files: completed", file=sys.stderr)
    sys.stderr.flush()

def get_pending_copies(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT uid, relative_path, size, last_modified FROM source_files
            WHERE (copy_status IS NULL OR copy_status='pending' OR copy_status='error' OR copy_status='in_progress')
        """)
        return cur.fetchall()

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
    import sys
    import time
    from pathlib import Path
    from threading import Lock
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    print(f"[DEBUG] copy_files: db_path={db_path}, src_roots={src_roots}, dst_roots={dst_roots}")
    sys.stderr.flush()
    uid_path = UidPath()
    checksum_cache = ChecksumCache(db_path, uid_path)
    src_roots = [str(Path(root).resolve()) for root in (src_roots or [])]
    reset_status_for_missing_files(db_path, dst_roots)
    time.sleep(0.1)
    pending = get_pending_copies(db_path)
    if not pending:
        return
    checksums_on_disk = set()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path FROM destination_files WHERE copy_status='done'")
        for uid, rel_path in cur.fetchall():
            abs_path = uid_path.reconstruct_path(uid, rel_path)
            if abs_path:
                chksum = checksum_cache.get(str(abs_path))
                if chksum:
                    checksums_on_disk.add(chksum)
    copied_checksums = set(checksums_on_disk)
    copied_lock = Lock()
    def process_copy(args):
        uid, rel_path, size, last_modified = args
        print(f"[DEBUG] process_copy: uid={uid}, rel_path={rel_path}, thread={threading.current_thread().name}", file=sys.stderr)
        sys.stderr.flush()
        # Always use UidPath to reconstruct the source file path
        src_file = uid_path.reconstruct_path(uid, rel_path)
        print(f"[DEBUG] src_file resolved to: {src_file}", file=sys.stderr)
        sys.stderr.flush()
        if not src_file or not src_file.exists():
            print(f"[DEBUG] Source file not found: {src_file}", file=sys.stderr)
            mark_copy_status(db_path, uid, rel_path, 'error', 'Source file not found for resume')
            return False
        checksum = checksum_cache.get_or_compute(str(src_file))
        print(f"[DEBUG] checksum for src_file: {checksum}", file=sys.stderr)
        sys.stderr.flush()
        if not checksum:
            mark_copy_status(db_path, uid, rel_path, 'error', 'No valid checksum in cache and cannot compute')
            logging.error(f"[AGENT][COPY] Skipped (no valid checksum and cannot compute): {rel_path}")
            return False
        with copied_lock:
            if checksum in copied_checksums:
                mark_copy_status(db_path, uid, rel_path, 'done')
                logging.info(f"[AGENT][COPY] Skipped (deduplication: already present on disk or copied this batch): {rel_path}")
                return True
            copied_checksums.add(checksum)
        # Use path-aware deduplication: only skip if checksum exists at any destination
        if checksum_cache.exists_at_destination(checksum):
            mark_copy_status(db_path, uid, rel_path, 'done')
            logging.info(f"[AGENT][COPY] Skipped (checksum already present on disk in destination): {rel_path}")
            return True
        for dst_root in dst_roots:
            dst_file = Path(dst_root) / rel_path
            print(f"[DEBUG] About to create parent dir: {dst_file.parent}", file=sys.stderr)
            sys.stderr.flush()
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] Parent dir exists: {dst_file.parent.exists()} (should be True)", file=sys.stderr)
            print(f"[DEBUG] About to copy: {src_file} -> {dst_file}", file=sys.stderr)
            sys.stderr.flush()
            mark_copy_status(db_path, uid, rel_path, 'in_progress')
            def log_progress(percent, copied, total):
                if percent % 10 == 0 or percent == 100:
                    logging.info(f"[AGENT][COPY][PROGRESS] {rel_path}: {percent}% ({copied}/{total} bytes)")
            src_checksum, dst_checksum = copy_file(src_file, dst_file, progress_callback=log_progress, show_progressbar=True)
            print(f"[DEBUG] Copy complete: {src_file} -> {dst_file} exists={dst_file.exists()} size={dst_file.stat().st_size if dst_file.exists() else 'N/A'}", file=sys.stderr)
            sys.stderr.flush()
            if src_checksum == dst_checksum == checksum:
                with sqlite3.connect(db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("""
                        INSERT INTO destination_files (uid, relative_path, size, last_modified, copy_status)
                        VALUES (?, ?, ?, ?, 'done')
                        ON CONFLICT(uid, relative_path) DO UPDATE SET
                            size=excluded.size,
                            last_modified=excluded.last_modified,
                            copy_status='done'
                    """, (uid, rel_path, size, last_modified))
                    conn.commit()
                mark_copy_status(db_path, uid, rel_path, 'done')
                print(f"[DEBUG] File copy verified and marked done: {dst_file}", file=sys.stderr)
                sys.stderr.flush()
                return True
            else:
                mark_copy_status(db_path, uid, rel_path, 'error', 'Checksum mismatch after copy')
                print(f"[DEBUG] Checksum mismatch after copy: src={src_checksum}, dst={dst_checksum}, expected={checksum}", file=sys.stderr)
                sys.stderr.flush()
                return False
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(process_copy, args) for args in pending]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Copying files"):
            f.result()  # Wait for each job to finish and propagate exceptions
