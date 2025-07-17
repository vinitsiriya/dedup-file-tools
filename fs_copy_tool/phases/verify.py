def verify_files(db_path, stage='shallow', reverify=False):
    """
    Unified verify function: runs shallow or deep verification based on stage.
    Args:
        db_path (str): Path to job database.
        stage (str): 'shallow' or 'deep'.
        reverify (bool): If True, clear previous verification results before running.
    """
    if stage == 'shallow':
        shallow_verify_files(db_path, reverify=reverify)
    else:
        deep_verify_files(db_path, reverify=reverify)
import logging
from fs_copy_tool.utils.robust_sqlite import RobustSqliteConn
import time
from pathlib import Path
from fs_copy_tool.utils.fileops import compute_sha256
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.uidpath import UidPath, UidPathUtil
from tqdm import tqdm

def shallow_verify_files(db_path, reverify=False, max_workers=8):
    """Shallow verification: check file existence, size, and last modified time. Now multithreaded."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    uid_path = UidPathUtil()
    uid_path.update_mounts()  # Ensure mounts are up to date for test environments
    logging.info("Starting shallow verification stage...")
    timestamp = int(time.time())
    from fs_copy_tool.main import get_checksum_db_path, connect_with_attached_checksum_db
    import os
    job_dir = os.path.dirname(db_path)
    checksum_db_path = get_checksum_db_path(job_dir)
    def conn_factory():
        return connect_with_attached_checksum_db(db_path, checksum_db_path)
    if reverify:
        with RobustSqliteConn(db_path).connect() as conn:
            conn.execute("DELETE FROM verification_shallow_results")
            conn.commit()
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.uid, s.relative_path, s.size, s.last_modified
            FROM source_files s
            JOIN copy_status cs ON s.uid = cs.uid AND s.relative_path = cs.relative_path
            WHERE cs.status='done'
        """)
        files = cur.fetchall()
    if not files:
        print("[INFO] No files found in source_files with copy_status='done'. Nothing to verify.")
        logging.warning("No files found in source_files with copy_status='done'. Nothing to verify.")
        return

    def verify_one(entry):
        uid, rel_path, expected_size, expected_last_modified = entry
        exists = 0
        size_matched = 0
        last_modified_matched = 0
        actual_size = None
        actual_last_modified = None
        verify_status = 'ok'
        verify_error = None
        uid_path_obj = UidPath(uid, rel_path)
        dst_file = uid_path.reconstruct_path(uid_path_obj)
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
        logging.info(f"Shallow verify {rel_path}: {verify_status}{' - ' + verify_error if verify_error else ''}")
        return (uid, rel_path, exists, size_matched, last_modified_matched, expected_size, actual_size, expected_last_modified, actual_last_modified, verify_status, verify_error, timestamp)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(verify_one, entry) for entry in files]
        from tqdm import tqdm
        for f in tqdm(as_completed(futures), total=len(futures), desc="Shallow Verify", unit="file"):
            results.append(f.result())
    # Write all results in main thread
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.executemany("""
            INSERT OR REPLACE INTO verification_shallow_results (uid, relative_path, "exists", size_matched, last_modified_matched, expected_size, actual_size, expected_last_modified, actual_last_modified, verify_status, verify_error, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, results)
        conn.commit()
    logging.info(f"Shallow verification complete: {len(files)} files processed.")

def deep_verify_files(db_path, reverify=False, max_workers=8):
    """Deep verification: always perform all shallow checks, then compare checksums. Now multithreaded."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    uid_path = UidPathUtil()
    uid_path.update_mounts()  # Ensure mounts are up to date for test environments
    logging.info("Starting deep verification stage...")
    timestamp = int(time.time())
    from fs_copy_tool.main import get_checksum_db_path, connect_with_attached_checksum_db
    import os
    job_dir = os.path.dirname(db_path)
    checksum_db_path = get_checksum_db_path(job_dir)
    def conn_factory():
        return connect_with_attached_checksum_db(db_path, checksum_db_path)
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    if reverify:
        with RobustSqliteConn(db_path).connect() as conn:
            conn.execute("DELETE FROM verification_deep_results")
            conn.commit()
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.uid, s.relative_path, s.size, s.last_modified
            FROM source_files s
            JOIN copy_status cs ON s.uid = cs.uid AND s.relative_path = cs.relative_path
            WHERE cs.status='done'
        """)
        files = cur.fetchall()
    if not files:
        print("[INFO] No files found in source_files with copy_status='done'. Nothing to verify.")
        logging.warning("No files found in source_files with copy_status='done'. Nothing to verify.")
        return

    def verify_one(entry):
        uid, rel_path, expected_size, expected_last_modified = entry
        exists = 0
        size_matched = 0
        last_modified_matched = 0
        actual_size = None
        actual_last_modified = None
        shallow_status = 'ok'
        shallow_error = None
        uid_path_obj = UidPath(uid, rel_path)
        dst_file = uid_path.reconstruct_path(uid_path_obj)
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
                shallow_status = 'mismatch'
                shallow_error = 'Size or last_modified mismatch'
        else:
            shallow_status = 'missing'
            shallow_error = 'File missing at destination'
        src_file = uid_path.reconstruct_path(uid_path_obj)
        dst_file_actual = uid_path.reconstruct_path(uid_path_obj)
        expected_checksum = checksum_cache.get(str(dst_file_actual)) if dst_file_actual else None
        checksum_matched = 0
        verify_status = 'ok'
        verify_error = None
        src_checksum = None
        dst_checksum = None
        if shallow_status != 'ok':
            verify_status = shallow_status
            verify_error = shallow_error
        else:
            if not src_file or not src_file.exists():
                verify_status = 'error'
                verify_error = 'Source file missing'
            elif not dst_file_actual or not dst_file_actual.exists():
                verify_status = 'error'
                verify_error = 'Destination file missing'
            else:
                src_checksum = checksum_cache.get_or_compute_with_invalidation(str(src_file))
                dst_checksum = checksum_cache.get_or_compute_with_invalidation(str(dst_file_actual))
                if src_checksum == dst_checksum == expected_checksum:
                    checksum_matched = 1
                else:
                    verify_status = 'failed'
                    verify_error = 'Checksum mismatch'
        logging.info(f"Deep verify {rel_path}: {verify_status}{' - ' + verify_error if verify_error else ''}")
        return (uid, rel_path, checksum_matched, expected_checksum, src_checksum, dst_checksum, verify_status, verify_error, timestamp)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(verify_one, entry) for entry in files]
        from tqdm import tqdm
        for f in tqdm(as_completed(futures), total=len(futures), desc="Deep Verify", unit="file"):
            results.append(f.result())
    # Write all results in main thread
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.executemany("""
            INSERT OR REPLACE INTO verification_deep_results (uid, relative_path, checksum_matched, expected_checksum, src_checksum, dst_checksum, verify_status, verify_error, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, results)
        conn.commit()
    logging.info(f"Deep verification complete: {len(files)} files processed.")
