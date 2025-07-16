import os
import sqlite3
import tempfile
import shutil
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

def test_insert_and_get(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    # Create a temp file
    file_path = tmp_path / "file1.txt"
    file_path.write_text("hello world")
    stat = file_path.stat()
    checksum = "dummychecksum123"
    cache.insert_or_update(str(file_path), stat.st_size, int(stat.st_mtime), checksum)
    # Should retrieve the checksum
    assert cache.get(str(file_path)) == checksum

def test_get_or_compute(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "file2.txt"
    file_path.write_text("abc123")
    # Should compute and cache
    checksum = cache.get_or_compute(str(file_path))
    assert checksum is not None
    # Should retrieve from cache now
    checksum2 = cache.get(str(file_path))
    assert checksum == checksum2

def test_exists(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "file3.txt"
    file_path.write_text("testdata")
    stat = file_path.stat()
    checksum = "existschecksum"
    cache.insert_or_update(str(file_path), stat.st_size, int(stat.st_mtime), checksum)
    assert cache.exists(checksum)
    assert not cache.exists("notfound")

def test_get_missing(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "missing.txt"
    # File does not exist in cache
    assert cache.get(str(file_path)) is None

def test_get_or_compute_missing_file(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    def conn_factory():
        conn = sqlite3.connect(db_path)
        conn.execute(f"ATTACH DATABASE '{db_path}' AS checksumdb")
        return conn
    cache = ChecksumCache(conn_factory, uid_path)
    file_path = tmp_path / "doesnotexist.txt"
    # File does not exist on disk
    assert cache.get_or_compute(str(file_path)) is None
