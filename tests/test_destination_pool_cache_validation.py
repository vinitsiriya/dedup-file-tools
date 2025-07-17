import os
import sqlite3
import tempfile
import shutil
import pytest
from pathlib import Path
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.uidpath import UidPathUtil
import time

def setup_destination_pool_db(tmp_path):
    db_path = tmp_path / "test_dest.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE destination_pool_files (
            uid TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            size INTEGER,
            last_modified INTEGER,
            last_seen INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    conn.execute("""
        CREATE TABLE checksum_cache (
            uid TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            size INTEGER,
            last_modified INTEGER,
            checksum TEXT,
            imported_at INTEGER,
            last_validated INTEGER,
            is_valid INTEGER DEFAULT 1,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    conn.commit()
    conn.close()
    return str(db_path)

def test_exists_at_destination_pool(tmp_path):
    db_path = setup_destination_pool_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    # Create a temp file and add to destination pool
    file_path = tmp_path / "destfile.txt"
    file_path.write_text("destination pool test")
    stat = file_path.stat()
    uid_path_obj = uid_path.convert_path(str(file_path))
    uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
    checksum = "destpoolchecksum"
    now = int(time.time())
    # Insert into destination_pool_files and checksum_cache
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO destination_pool_files (uid, relative_path, size, last_modified, last_seen) VALUES (?, ?, ?, ?, ?)",
                     (uid, rel_path, stat.st_size, int(stat.st_mtime), now))
        conn.execute("INSERT INTO checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                     (uid, rel_path, stat.st_size, int(stat.st_mtime), checksum, now, now))
        conn.commit()
    # Should validate as True
    assert cache.exists_at_destination_pool(checksum)
    # Remove file, should invalidate and return False
    file_path.unlink()
    assert not cache.exists_at_destination_pool(checksum)
    # Recreate file with wrong size
    file_path.write_text("wrong size!")
    assert not cache.exists_at_destination_pool(checksum)
    # Restore correct size but wrong mtime
    file_path.write_text("destination pool test")
    os.utime(file_path, (stat.st_atime, stat.st_mtime + 100))
    assert not cache.exists_at_destination_pool(checksum)
    # Restore correct mtime and size
    os.utime(file_path, (stat.st_atime, stat.st_mtime))
    assert not cache.exists_at_destination_pool(checksum)  # cache is now invalid
