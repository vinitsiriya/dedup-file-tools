
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
    uid_path = UidPathUtil()
    checksum_db_path = get_checksum_db_path(os.path.dirname(db_path))
    def conn_factory():
        return connect_with_attached_checksum_db(db_path, checksum_db_path)
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    with connect_with_attached_checksum_db(db_path, checksum_db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, move_to_uid, move_to_rel_path, status, checksum FROM dedup_move_plan WHERE status='moved'")
        rows = cur.fetchall()
    from concurrent.futures import ThreadPoolExecutor
    from tqdm import tqdm
    from collections import deque
    def verify_one(args):
        uid, rel_path, move_to_uid, move_to_rel_path, status, expected_checksum = args
        if move_to_uid and move_to_rel_path:
            dst_uid_path = UidPath(move_to_uid, move_to_rel_path)
        else:
            dst_uid_path = UidPath(uid, rel_path)
        dst_path = uid_path.reconstruct_path(dst_uid_path)
        error_message = None
        verified = False
        if not dst_path or not dst_path.exists():
            error_message = 'File missing after move'
        else:
            try:
                stat = dst_path.stat()
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
