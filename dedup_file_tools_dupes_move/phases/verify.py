
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
    for uid, rel_path, move_to_uid, move_to_rel_path, status, expected_checksum in rows:
        # Reconstruct destination path using UidPath
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
            # Check file size
            try:
                stat = dst_path.stat()
                # Optionally, verify checksum
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
                logging.info(f"Verified moved file: {dst_path}")
            else:
                cur2.execute("""
                    UPDATE dedup_move_plan SET status='error', error_message=?, updated_at=? WHERE uid=? AND relative_path=?
                """, (error_message, int(time.time()), uid, rel_path))
                cur2.execute("""
                    INSERT INTO dedup_move_history (uid, relative_path, attempted_at, action, result, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uid, rel_path, int(time.time()), 'verify', 'error', error_message))
                logging.error(f"Verification failed for {dst_path}: {error_message}")
