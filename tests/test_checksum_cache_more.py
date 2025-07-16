import os
import sqlite3
import tempfile
import pytest
from pathlib import Path
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.uidpath import UidPathUtil

def setup_test_db_with_pool(tmp_path):
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
    conn.commit()
    conn.close()
    return str(db_path)

def test_exists_at_destination_pool(tmp_path):
    db_path = setup_test_db_with_pool(tmp_path)
    uid_path = UidPathUtil()
    cache = ChecksumCache(db_path, uid_path)
    # Create a temp file and add to both tables
    file_path = tmp_path / "file1.txt"
    file_path.write_text("hello world")
    stat = file_path.stat()
    checksum = "dummychecksum123"
    uid_path_obj = uid_path.convert_path(str(file_path))
    uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
    # Add to destination_pool_files
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO destination_pool_files (uid, relative_path, size, last_modified, last_seen) VALUES (?, ?, ?, ?, 0)", (uid, str(rel), stat.st_size, int(stat.st_mtime)))
        conn.execute("INSERT INTO checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid) VALUES (?, ?, ?, ?, ?, 0, 0, 1)", (uid, str(rel), stat.st_size, int(stat.st_mtime), checksum))
        conn.commit()
    # Should find the checksum in the pool
    assert cache.exists_at_destination_pool(checksum)
    # Should not find a random checksum
    assert not cache.exists_at_destination_pool("not_a_real_checksum")

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

def test_update_existing_entry(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    cache = ChecksumCache(db_path, uid_path)
    file_path = tmp_path / "file_update.txt"
    file_path.write_text("first")
    stat = file_path.stat()
    cache.insert_or_update(str(file_path), stat.st_size, int(stat.st_mtime), "checksum1")
    # Update file and checksum
    file_path.write_text("second")
    stat = file_path.stat()
    cache.insert_or_update(str(file_path), stat.st_size, int(stat.st_mtime), "checksum2")
    assert cache.get(str(file_path)) == "checksum2"

def test_multiple_files_and_uids(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    cache = ChecksumCache(db_path, uid_path)
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file1.write_text("a")
    file2.write_text("b")
    stat1 = file1.stat()
    stat2 = file2.stat()
    cache.insert_or_update(str(file1), stat1.st_size, int(stat1.st_mtime), "c1")
    cache.insert_or_update(str(file2), stat2.st_size, int(stat2.st_mtime), "c2")
    assert cache.get(str(file1)) == "c1"
    assert cache.get(str(file2)) == "c2"

def test_invalid_entries_are_ignored(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    cache = ChecksumCache(db_path, uid_path)
    file_path = tmp_path / "file_invalid.txt"
    file_path.write_text("data")
    stat = file_path.stat()
    # Insert valid
    cache.insert_or_update(str(file_path), stat.st_size, int(stat.st_mtime), "validsum")
    # Manually mark as invalid
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE checksum_cache SET is_valid=0 WHERE checksum=?", ("validsum",))
        conn.commit()
    assert cache.get(str(file_path)) is None
    assert not cache.exists("validsum")

def test_subdirectory_file(tmp_path):
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    cache = ChecksumCache(db_path, uid_path)
    subdir = tmp_path / "sub1" / "sub2"
    subdir.mkdir(parents=True)
    file_path = subdir / "deep.txt"
    file_path.write_text("deepdata")
    stat = file_path.stat()
    cache.insert_or_update(str(file_path), stat.st_size, int(stat.st_mtime), "deepchk")
    assert cache.get(str(file_path)) == "deepchk"
