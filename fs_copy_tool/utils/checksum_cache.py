import sqlite3
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

    def get_or_compute_with_invalidation(self, path: str) -> Optional[str]:
        """
        Get checksum from cache if file exists and size/mtime match; otherwise, recompute and update cache.
        """
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return None
        file_path = Path(path)
        if not file_path.exists():
            return None
        stat = file_path.stat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT checksum, size, last_modified, is_valid FROM checksum_cache WHERE uid=? AND relative_path=? ORDER BY last_validated DESC LIMIT 1",
                (uid, str(rel_path))
            )
            row = cur.fetchone()
        if row and row[0] and row[3] == 1:
            cached_checksum, cached_size, cached_mtime, _ = row
            if cached_size == stat.st_size and cached_mtime == int(stat.st_mtime):
                return cached_checksum
        # If not valid or file changed, recompute and update
        checksum = compute_sha256(file_path)
        if checksum:
            self.insert_or_update(path, stat.st_size, int(stat.st_mtime), checksum)
        return checksum

    def exists_at_destination_pool(self, checksum: str) -> bool:
        """
        Check if the given checksum exists and is valid at any file in the destination pool.
        Uses a SQL JOIN for efficiency.
        """
        with sqlite3.connect(self.db_path) as conn:
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
        
    def exists_at_destination_pool(self, checksum: str) -> bool:
        """
        Check if the given checksum exists and is valid at any file in the destination pool.
        Uses a SQL JOIN for efficiency.
        """
        with sqlite3.connect(self.db_path) as conn:
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
    """
    Centralized access for all checksum cache operations.
    Uses UidPath for all conversions and file resolution.
    """
    def __init__(self, db_path: str, uid_path):
        self.db_path = db_path
        self.uid_path = uid_path

    def get(self, path: str) -> Optional[str]:
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT checksum, is_valid FROM checksum_cache WHERE uid=? AND relative_path=? ORDER BY last_validated DESC LIMIT 1",
                (uid, str(rel_path))
            )
            row = cur.fetchone()
            if row and row[0] and row[1] == 1:
                return row[0]
        return None

    def exists(self, checksum: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM checksum_cache WHERE checksum=? AND is_valid=1 LIMIT 1",
                (checksum,)
            )
            return cur.fetchone() is not None

    def insert_or_update(self, path: str, size: int, last_modified: int, checksum: str):
        uid_path_obj = self.uid_path.convert_path(path)
        uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
        if not uid:
            return
        now = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
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
        """
        Get checksum from cache, or compute, update, and return it if missing.
        """
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

    def exists_at_paths(self, paths, checksum):
        """
        Check if the given checksum exists and is valid at any of the specified paths.
        Args:
            paths (list of str): List of absolute file paths to check.
            checksum (str): The checksum to look for.
        Returns:
            bool: True if the checksum exists at any of the given paths, False otherwise.
        """
        for path in paths:
            uid_path_obj = self.uid_path.convert_path(path)
            uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
            if not uid:
                continue
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM checksum_cache WHERE uid=? AND relative_path=? AND checksum=? AND is_valid=1 LIMIT 1",
                    (uid, str(rel_path), checksum)
                )
                if cur.fetchone():
                    return True
        return False

    def exists_at_uid_relpath_array(self, uid_relpath_list, checksum):
        """
        Check if the given checksum exists and is valid at any of the specified (uid, rel_path) pairs.
        Args:
            uid_relpath_list (list of (uid, rel_path)): List of (uid, rel_path) tuples to check.
            checksum (str): The checksum to look for.
        Returns:
            bool: True if the checksum exists at any of the given (uid, rel_path) pairs, False otherwise.
        """
        for uid, rel_path in uid_relpath_list:
            if not uid:
                continue
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM checksum_cache WHERE uid=? AND relative_path=? AND checksum=? AND is_valid=1 LIMIT 1",
                    (uid, str(rel_path), checksum)
                )
                if cur.fetchone():
                    return True
        return False

    def exists_at_destination(self, uid, rel_path):
        """
        Check if a file exists at the given (uid, rel_path) in the destination_files table and is marked as done.
        Args:
            uid (str): UID of the volume.
            rel_path (str): Relative path from the mount point.
        Returns:
            bool: True if the file exists and is marked as done in destination_files, False otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM destination_files WHERE uid=? AND relative_path=? AND copy_status='done' LIMIT 1",
                (uid, str(rel_path))
            )
            return cur.fetchone() is not None

    def exists_at_destination(self, checksum):
        """
        Check if any file in the destination_files table is marked as done and has the given checksum in the checksum_cache.
        Args:
            checksum (str): The checksum to look for.
        Returns:
            bool: True if any destination file is marked as done and has the given checksum, False otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT 1 FROM destination_files d
                JOIN checksum_cache c ON d.uid = c.uid AND d.relative_path = c.relative_path
                WHERE d.copy_status = 'done' AND c.checksum = ? AND c.is_valid = 1
                LIMIT 1
                """,
                (checksum,)
            )
            return cur.fetchone() is not None

    def ensure_indexes(self):
        """
        Ensure indexes exist on (uid, relative_path) and (checksum, is_valid) for fast lookups.
        Should be called once after DB creation or migration.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("CREATE INDEX IF NOT EXISTS idx_checksum_cache_uid_relpath ON checksum_cache(uid, relative_path)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_checksum_cache_checksum_valid ON checksum_cache(checksum, is_valid)")
            conn.commit()
