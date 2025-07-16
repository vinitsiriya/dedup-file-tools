import sqlite3
import pytest
from pathlib import Path
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.uidpath import UidPathUtil

def setup_test_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
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

def test_get_or_compute_with_invalidation_basic(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello world")
    # First call should compute and cache
    checksum1 = cache.get_or_compute_with_invalidation(str(file_path))
    assert checksum1 is not None
    # Second call should retrieve from cache
    checksum2 = cache.get_or_compute_with_invalidation(str(file_path))
    assert checksum1 == checksum2

def test_get_or_compute_with_invalidation_file_changed(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("first")
    checksum1 = cache.get_or_compute_with_invalidation(str(file_path))
    assert checksum1 is not None
    # Change file contents
    file_path.write_text("second")
    checksum2 = cache.get_or_compute_with_invalidation(str(file_path))
    assert checksum2 is not None
    assert checksum1 != checksum2

def test_get_or_compute_with_invalidation_file_metadata_changed(tmp_path):
    import time
    import os
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("meta test")
    checksum1 = cache.get_or_compute_with_invalidation(str(file_path))
    assert checksum1 is not None
    # Change mtime
    new_mtime = int(file_path.stat().st_mtime) + 10
    os.utime(file_path, (new_mtime, new_mtime))
    checksum2 = cache.get_or_compute_with_invalidation(str(file_path))
    assert checksum2 == checksum1  # Content unchanged, checksum same

def test_get_or_compute_with_invalidation_missing_file(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "missing.txt"
    assert cache.get_or_compute_with_invalidation(str(file_path)) is None
