from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
import time

class DestinationPoolIndex:
    """
    Manages the destination pool index for global duplicate detection.
    This does NOT store checksums, only tracks which files are in the pool (by uid and relative path).
    Checksum management remains in checksum_cache.py.
    """
    def __init__(self, uid_path):
        self.uid_path = uid_path

    def add_or_update_file(self, conn, path: str, size: int, last_modified: int):
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return
        now = int(time.time())
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO destination_pool_files (uid, relative_path, size, last_modified, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(uid, relative_path) DO UPDATE SET
                size=excluded.size,
                last_modified=excluded.last_modified,
                last_seen=excluded.last_seen
            """,
            (uid, str(rel_path), size, last_modified, now)
        )
        conn.commit()

    def exists(self, conn, uid: str, rel_path: str) -> bool:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM destination_pool_files WHERE uid=? AND relative_path=? LIMIT 1",
            (uid, rel_path)
        )
        return cur.fetchone() is not None

    def all_files(self, conn):
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM destination_pool_files")
        return cur.fetchall()

    # Add more pool management methods as needed
