import logging
import sqlite3
import time
from pathlib import Path
from fs_copy_tool.utils.fileops import compute_sha256
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.uidpath import UidPath

def shallow_verify_files(db_path, src_roots, dst_roots):
    """Shallow verification: check existence, size, last_modified."""
    logging.info("Starting shallow verification stage...")
    timestamp = int(time.time())
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM destination_files WHERE copy_status='done'")
        files = cur.fetchall()
    for uid, rel_path, expected_size, expected_last_modified in files:
        exists = 0
        size_matched = 0
        last_modified_matched = 0
        actual_size = None
        actual_last_modified = None
        verify_status = 'ok'
        verify_error = None
        dst_file = None
        for dst_root in dst_roots:
            candidate = Path(dst_root) / rel_path
            if candidate.exists():
                dst_file = candidate
                break
        if dst_file and dst_file.exists():
            exists = 1
            stat = dst_file.stat()
            actual_size = stat.st_size
            actual_last_modified = int(stat.st_mtime)
            if actual_size == expected_size:
                size_matched = 1
            if actual_last_modified == int(expected_last_modified):
                last_modified_matched = 1
            if not (size_matched and last_modified_matched):
                verify_status = 'mismatch'
                verify_error = 'Size or last_modified mismatch'
        else:
            verify_status = 'missing'
            verify_error = 'File missing at destination'
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO verification_shallow_results (uid, relative_path, "exists", size_matched, last_modified_matched, expected_size, actual_size, expected_last_modified, actual_last_modified, verify_status, verify_error, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, rel_path, exists, size_matched, last_modified_matched, expected_size, actual_size, expected_last_modified, actual_last_modified, verify_status, verify_error, timestamp))
            conn.commit()
        logging.info(f"Shallow verify {rel_path}: {verify_status}{' - ' + verify_error if verify_error else ''}")

def deep_verify_files(db_path, src_roots, dst_roots):
    """Deep verification: compare checksums between source and destination, using cache as the only source of truth."""
    logging.info("Starting deep verification stage...")
    timestamp = int(time.time())
    uid_path = UidPath()
    checksum_cache = ChecksumCache(db_path, uid_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM destination_files WHERE copy_status='done'")
        files = cur.fetchall()
    for uid, rel_path, size, last_modified in files:
        dst_file = uid_path.reconstruct_path(uid, rel_path)
        expected_checksum = checksum_cache.get(str(dst_file)) if dst_file else None
        checksum_matched = 0
        verify_status = 'ok'
        verify_error = None
        src_file = None
        dst_file_actual = None
        src_checksum = None
        dst_checksum = None
        for src_root in src_roots:
            candidate = Path(src_root) / rel_path
            if candidate.exists():
                src_file = candidate
                break
        for dst_root in dst_roots:
            candidate = Path(dst_root) / rel_path
            if candidate.exists():
                dst_file_actual = candidate
                break
        if not src_file or not src_file.exists():
            verify_status = 'error'
            verify_error = 'Source file missing'
        elif not dst_file_actual or not dst_file_actual.exists():
            verify_status = 'error'
            verify_error = 'Destination file missing'
        else:
            src_checksum = checksum_cache.get_or_compute(str(src_file))
            dst_checksum = checksum_cache.get_or_compute(str(dst_file_actual))
            if src_checksum == dst_checksum == expected_checksum:
                checksum_matched = 1
            else:
                verify_status = 'failed'
                verify_error = 'Checksum mismatch'
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO verification_deep_results (uid, relative_path, checksum_matched, expected_checksum, src_checksum, dst_checksum, verify_status, verify_error, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (uid, rel_path, checksum_matched, expected_checksum, src_checksum, dst_checksum, verify_status, verify_error, timestamp))
            conn.commit()
        logging.info(f"Deep verify {rel_path}: {verify_status}{' - ' + verify_error if verify_error else ''}")
