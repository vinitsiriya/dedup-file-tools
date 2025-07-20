from dedup_file_tools_commons.utils.fileops import compute_sha256
from pathlib import Path
from typing import Optional
import time

class ChecksumCache2:
    """
    Variant of ChecksumCache that takes a live DB connection object for all operations.
    This avoids opening/closing a connection for each query, and is suitable for batch operations.
    """
    def __init__(self, uid_path):
        self.uid_path = uid_path

    def exists_at_paths(self, conn, paths, checksum):
        for path in paths:
            uid_path_obj = self.uid_path.convert_path(path)
            uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
            if not uid:
                continue
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=? AND checksum=? AND is_valid=1 LIMIT 1",
                (uid, str(rel_path), checksum)
            )
            if cur.fetchone():
                return True
        return False

    def exists_at_uid_relpath_array(self, conn, uid_relpath_list, checksum):
        for uid, rel_path in uid_relpath_list:
            if not uid:
                continue
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=? AND checksum=? AND is_valid=1 LIMIT 1",
                (uid, str(rel_path), checksum)
            )
            if cur.fetchone():
                return True
        return False

    def exists_at_destination(self, conn, uid, rel_path):
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM destination_files WHERE uid=? AND relative_path=? LIMIT 1",
            (uid, str(rel_path))
        )
        return cur.fetchone() is not None

    def exists_at_destination_checksum(self, conn, checksum):
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

    def ensure_indexes(self, conn):
        cur = conn.cursor()
        cur.execute("CREATE INDEX IF NOT EXISTS idx_checksum_cache_uid_relpath ON checksumdb.checksum_cache(uid, relative_path)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_checksum_cache_checksum_valid ON checksumdb.checksum_cache(checksum, is_valid)")
        conn.commit()

    def get_or_compute_with_invalidation(self, conn, path: str) -> Optional[str]:
        import logging
        logging.info(f"[ChecksumCache2] get_or_compute_with_invalidation called for {path}")
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            logging.info(f"[ChecksumCache2] No UID for path: {path}")
            return None
        file_path = Path(path)
        if not file_path.exists():
            logging.info(f"[ChecksumCache2] File does not exist: {file_path}")
            return None
        stat = file_path.stat()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT checksum, size, last_modified, is_valid FROM checksum_cache WHERE uid=? AND relative_path=? ORDER BY last_validated DESC LIMIT 1",
                (uid, str(rel_path))
            )
            row = cur.fetchone()
            logging.info(f"[ChecksumCache2] Cache query result for {file_path}: {row}")
        except Exception as e:
            logging.error(f"[ChecksumCache2] Exception during cache query for {file_path}: {e}")
            return None
        if row and row[0] and row[3] == 1:
            cached_checksum, cached_size, cached_mtime, _ = row
            if cached_size == stat.st_size and cached_mtime == int(stat.st_mtime):
                logging.info(f"[ChecksumCache2] Cache hit for {file_path}: {cached_checksum}")
                return cached_checksum
        logging.info(f"[ChecksumCache2] No valid cache, computing checksum for {file_path}")
        checksum = compute_sha256(file_path)
        logging.info(f"[ChecksumCache2] Computed checksum for {file_path}: {checksum}")
        if checksum:
            self.insert_or_update(conn, path, stat.st_size, int(stat.st_mtime), checksum)
        return checksum

    def exists_at_destination_pool(self, conn, checksum: str) -> bool:
        import logging
        cur = conn.cursor()
        cur.execute(
            """
            SELECT dpf.uid, dpf.relative_path, dpf.size, dpf.last_modified, cc.is_valid
            FROM destination_pool_files AS dpf
            JOIN checksumdb.checksum_cache AS cc
              ON dpf.uid = cc.uid AND dpf.relative_path = cc.relative_path
            WHERE cc.checksum = ? AND cc.is_valid = 1
            LIMIT 1
            """,
            (checksum,)
        )
        row = cur.fetchone()
        if not row:
            logging.info(f"[ChecksumCache2] No destination pool entry for checksum {checksum}")
            return False
        uid, rel_path, cached_size, cached_mtime, is_valid = row
        from dedup_file_tools_commons.utils.uidpath import UidPath
        uid_path_obj = UidPath(uid, rel_path)
        file_path = self.uid_path.reconstruct_path(uid_path_obj)
        if not file_path or not Path(file_path).exists():
            logging.warning(f"[ChecksumCache2] Destination pool file missing: uid={uid}, rel_path={rel_path}, path={file_path}")
            cur.execute(
                "UPDATE checksumdb.checksum_cache SET is_valid=0 WHERE uid=? AND relative_path=?",
                (uid, rel_path)
            )
            conn.commit()
            return False
        stat = Path(file_path).stat()
        if stat.st_size != cached_size:
            logging.warning(f"[ChecksumCache2] Destination pool file size mismatch: {file_path} (disk={stat.st_size}, cache={cached_size})")
            cur.execute(
                "UPDATE checksumdb.checksum_cache SET is_valid=0 WHERE uid=? AND relative_path=?",
                (uid, rel_path)
            )
            conn.commit()
            return False
        if int(stat.st_mtime) != cached_mtime:
            logging.warning(f"[ChecksumCache2] Destination pool file mtime mismatch: {file_path} (disk={int(stat.st_mtime)}, cache={cached_mtime})")
            cur.execute(
                "UPDATE checksumdb.checksum_cache SET is_valid=0 WHERE uid=? AND relative_path=?",
                (uid, rel_path)
            )
            conn.commit()
            return False
        logging.info(f"[ChecksumCache2] Destination pool file valid: {file_path}")
        return True

    def get(self, conn, path: str) -> Optional[str]:
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return None
        cur = conn.cursor()
        cur.execute(
            "SELECT checksum, is_valid FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=? ORDER BY last_validated DESC LIMIT 1",
            (uid, str(rel_path))
        )
        row = cur.fetchone()
        if row and row[0] and row[1] == 1:
            return row[0]
        return None

    def exists(self, conn, checksum: str) -> bool:
        cur = conn.cursor()
        cur.execute(
            "SELECT 1 FROM checksumdb.checksum_cache WHERE checksum=? AND is_valid=1 LIMIT 1",
            (checksum,)
        )
        return cur.fetchone() is not None

    def insert_or_update(self, conn, path: str, size: int, last_modified: int, checksum: str):
        import logging
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            logging.info(f"[ChecksumCache2] Skipping insert: No UID for path {path}")
            return
        now = int(time.time())
        logging.info(f"[ChecksumCache2] Inserting checksum: uid={uid}, rel_path={rel_path}, size={size}, mtime={last_modified}, checksum={checksum}")
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

    def get_or_compute(self, conn, path: str) -> Optional[str]:
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return None
        checksum = self.get(conn, path)
        if checksum:
            return checksum
        file_path = Path(path)
        if not file_path.exists():
            return None
        stat = file_path.stat()
        checksum = compute_sha256(file_path)
        if checksum:
            self.insert_or_update(conn, path, stat.st_size, int(stat.st_mtime), checksum)
        return checksum
