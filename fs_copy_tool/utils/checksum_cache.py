from fs_copy_tool.utils.robust_sqlite import RobustSqliteConn
from typing import Optional
from pathlib import Path
from fs_copy_tool.utils.fileops import compute_sha256
import time

   
import sqlite3
from typing import Optional
from pathlib import Path
from fs_copy_tool.utils.fileops import compute_sha256
import time


class ChecksumCache:
    """
    Centralized access for all checksum cache operations.
    Uses UidPath for all conversions and file resolution.
    """
    def __init__(self, conn_factory, uid_path):
        self.conn_factory = conn_factory
        self.uid_path = uid_path

    def exists_at_paths(self, paths, checksum):
        for path in paths:
            uid_path_obj = self.uid_path.convert_path(path)
            uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
            if not uid:
                continue
            with self.conn_factory() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=? AND checksum=? AND is_valid=1 LIMIT 1",
                    (uid, str(rel_path), checksum)
                )
                if cur.fetchone():
                    return True
        return False

    def exists_at_uid_relpath_array(self, uid_relpath_list, checksum):
        for uid, rel_path in uid_relpath_list:
            if not uid:
                continue
            with self.conn_factory() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=? AND checksum=? AND is_valid=1 LIMIT 1",
                    (uid, str(rel_path), checksum)
                )
                if cur.fetchone():
                    return True
        return False

    def exists_at_destination(self, uid, rel_path):
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM destination_files WHERE uid=? AND relative_path=? LIMIT 1",
                (uid, str(rel_path))
            )
            return cur.fetchone() is not None

    def exists_at_destination_checksum(self, checksum):
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 1 FROM destination_files d
                JOIN checksumdb.checksum_cache c ON d.uid = c.uid AND d.relative_path = c.relative_path
                WHERE c.checksum = ? AND c.is_valid = 1
                LIMIT 1
                """,
                (checksum,)
            )
            return cur.fetchone() is not None

    def ensure_indexes(self):
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute("CREATE INDEX IF NOT EXISTS idx_checksum_cache_uid_relpath ON checksumdb.checksum_cache(uid, relative_path)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_checksum_cache_checksum_valid ON checksumdb.checksum_cache(checksum, is_valid)")
            conn.commit()

    def get_or_compute_with_invalidation(self, path: str) -> Optional[str]:
        import logging
        logging.info(f"[ChecksumCache] get_or_compute_with_invalidation called for {path}")
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            logging.info(f"[ChecksumCache] No UID for path: {path}")
            return None
        file_path = Path(path)
        if not file_path.exists():
            logging.info(f"[ChecksumCache] File does not exist: {file_path}")
            return None
        stat = file_path.stat()
        try:
            with self.conn_factory() as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT checksum, size, last_modified, is_valid FROM checksum_cache WHERE uid=? AND relative_path=? ORDER BY last_validated DESC LIMIT 1",
                    (uid, str(rel_path))
                )
                row = cur.fetchone()
            logging.info(f"[ChecksumCache] Cache query result for {file_path}: {row}")
        except Exception as e:
            logging.error(f"[ChecksumCache] Exception during cache query for {file_path}: {e}")
            return None
        if row and row[0] and row[3] == 1:
            cached_checksum, cached_size, cached_mtime, _ = row
            if cached_size == stat.st_size and cached_mtime == int(stat.st_mtime):
                logging.info(f"[ChecksumCache] Cache hit for {file_path}: {cached_checksum}")
                return cached_checksum
        logging.info(f"[ChecksumCache] No valid cache, computing checksum for {file_path}")
        checksum = compute_sha256(file_path)
        logging.info(f"[ChecksumCache] Computed checksum for {file_path}: {checksum}")
        if checksum:
            self.insert_or_update(path, stat.st_size, int(stat.st_mtime), checksum)
        return checksum

    def exists_at_destination_pool(self, checksum: str) -> bool:
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 1 FROM destination_pool_files AS dpf
                JOIN checksumdb.checksum_cache AS cc
                  ON dpf.uid = cc.uid AND dpf.relative_path = cc.relative_path
                WHERE cc.checksum = ? AND cc.is_valid = 1
                LIMIT 1
                """,
                (checksum,)
            )
            return cur.fetchone() is not None

    def get(self, path: str) -> Optional[str]:
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return None
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT checksum, is_valid FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=? ORDER BY last_validated DESC LIMIT 1",
                (uid, str(rel_path))
            )
            row = cur.fetchone()
            if row and row[0] and row[1] == 1:
                return row[0]
        return None

    def exists(self, checksum: str) -> bool:
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM checksumdb.checksum_cache WHERE checksum=? AND is_valid=1 LIMIT 1",
                (checksum,)
            )
            return cur.fetchone() is not None

    def insert_or_update(self, path: str, size: int, last_modified: int, checksum: str):
        import logging
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            logging.info(f"[ChecksumCache] Skipping insert: No UID for path {path}")
            return
        now = int(time.time())
        logging.info(f"[ChecksumCache] Inserting checksum: uid={uid}, rel_path={rel_path}, size={size}, mtime={last_modified}, checksum={checksum}")
        with self.conn_factory() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(uid, relative_path) DO UPDATE SET
                    size=excluded.size,
                    last_modified=excluded.last_modified,
                    checksum=excluded.checksum,
                    last_validated=excluded.last_validated,
                    is_valid=1
                """,
                (uid, str(rel_path), size, last_modified, checksum, now, now)
            )
            conn.commit()

    def get_or_compute(self, path: str) -> Optional[str]:
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return None
        checksum = self.get(path)
        if checksum:
            return checksum
        file_path = Path(path)
        if not file_path.exists():
            return None
        stat = file_path.stat()
        checksum = compute_sha256(file_path)
        if checksum:
            self.insert_or_update(path, stat.st_size, int(stat.st_mtime), checksum)
        return checksum

    # --- Duplicated/legacy methods restored for compatibility ---
    def exists_at_destination_pool_legacy(self, checksum: str) -> bool:
        # This is the legacy version using db_path, kept for compatibility if needed
        # It is not used in the new architecture but is preserved as per user instruction
        # It will raise if db_path is not set
        if not hasattr(self, 'db_path'):
            raise AttributeError('db_path not set on ChecksumCache')
        with RobustSqliteConn(self.db_path).connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 1 FROM destination_pool_files AS dpf
                JOIN checksum_cache AS cc
                  ON dpf.uid = cc.uid AND dpf.relative_path = cc.relative_path
                WHERE cc.checksum = ? AND cc.is_valid = 1
                LIMIT 1
                """,
                (checksum,)
            )
            return cur.fetchone() is not None


