
import os
import time
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def verify_moves(db_path, dst_root, threads=4):
    from dedup_file_tools_commons.utils.uidpath import UidPath, UidPathUtil
    from dedup_file_tools_commons.utils.paths import get_checksum_db_path
    from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
    from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
    import logging
    import time
    import sqlite3
    # If dst_root is None, load from job_metadata
    if dst_root is None:
        meta_db_path = db_path
        with sqlite3.connect(meta_db_path) as conn_meta:
            cur_meta = conn_meta.cursor()
            cur_meta.execute("SELECT value FROM job_metadata WHERE key='dupes_folder' LIMIT 1")
            row = cur_meta.fetchone()
            if row:
                dst_root = row[0]
            else:
                raise RuntimeError("dupes_folder not found in job_metadata. Please specify dupes_folder.")
    uid_path = UidPathUtil()
    checksum_db_path = get_checksum_db_path(os.path.dirname(db_path))
    def conn_factory():
        return connect_with_attached_checksum_db(db_path, checksum_db_path)
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    with connect_with_attached_checksum_db(db_path, checksum_db_path) as conn:
        cur = conn.cursor()
        # Also fetch pool_base_path for each file, for both moved and keeper
        cur.execute("""
            SELECT dmp.uid, dmp.relative_path, dmp.move_to_uid, dmp.move_to_rel_path, dmp.status, dmp.checksum, dfp.pool_base_path
            FROM dedup_move_plan dmp
            JOIN dedup_files_pool dfp ON dmp.uid = dfp.uid AND dmp.relative_path = dfp.relative_path
            WHERE dmp.status IN ('moved', 'keeper')
        """)
        rows = cur.fetchall()
    from concurrent.futures import ThreadPoolExecutor
    from tqdm import tqdm
    from collections import deque
    def verify_one(args):
        uid, rel_path, move_to_uid, move_to_rel_path, status, expected_checksum, pool_base_path = args
        # For moved files, verify in removal dir; for keeper, verify in original location
        src_path = uid_path.reconstruct_path(UidPath(uid, rel_path))
        if status == 'moved':
            try:
                rel_to_pool = os.path.relpath(src_path, pool_base_path)
            except Exception as e:
                rel_to_pool = rel_path  # fallback
            dst_path = os.path.join(dst_root, rel_to_pool)
        else:  # keeper
            dst_path = src_path
        error_message = None
        verified = False
        if not os.path.exists(dst_path):
            error_message = 'File missing after move'
        else:
            try:
                stat = os.stat(dst_path)
                actual_checksum = checksum_cache.get_or_compute_with_invalidation(str(dst_path))
                if actual_checksum != expected_checksum:
                    error_message = f'Checksum mismatch: expected {expected_checksum}, got {actual_checksum}'
                else:
                    verified = True
            except Exception as e:
                error_message = f'Error verifying file: {e}'
        with connect_with_attached_checksum_db(db_path, checksum_db_path) as conn2:
            cur2 = conn2.cursor()
            if verified:
                cur2.execute("""
                    UPDATE dedup_move_plan SET status='verified', error_message=NULL, updated_at=? WHERE uid=? AND relative_path=?
                """, (int(time.time()), uid, rel_path))
                cur2.execute("""
                    INSERT INTO dedup_move_history (uid, relative_path, attempted_at, action, result, error_message)
                    VALUES (?, ?, ?, ?, ?, NULL)
                """, (uid, rel_path, int(time.time()), 'verify', 'verified'))
                return (uid, rel_path, None)
            else:
                cur2.execute("""
                    UPDATE dedup_move_plan SET status='error', error_message=?, updated_at=? WHERE uid=? AND relative_path=?
                """, (error_message, int(time.time()), uid, rel_path))
                cur2.execute("""
                    INSERT INTO dedup_move_history (uid, relative_path, attempted_at, action, result, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uid, rel_path, int(time.time()), 'verify', 'error', error_message))
                return (uid, rel_path, error_message)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = deque()
        row_iter = iter(rows)
        for _ in range(min(threads * 2, len(rows))):
            try:
                row = next(row_iter)
                futures.append((executor.submit(verify_one, row), row))
            except StopIteration:
                break
        pbar = tqdm(total=len(rows), desc="Verifying moves", unit="file")
        completed = 0
        while futures:
            future, row = futures.popleft()
            try:
                uid, rel_path, err = future.result()
                if err:
                    logging.error(f"Verify error for {uid}:{rel_path}: {err}")
            except Exception as e:
                logging.error(f"Thread failed for {row[0]}:{row[1]}: {e}")
            completed += 1
            pbar.update(1)
            try:
                next_row = next(row_iter)
                futures.append((executor.submit(verify_one, next_row), next_row))
            except StopIteration:
                pass
        pbar.close()
