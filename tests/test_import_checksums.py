import sqlite3
import tempfile
import os
from fs_copy_tool.db import init_db
from fs_copy_tool.phases.checksum import import_checksums_from_old_db, import_checksums_to_cache

def make_db_with_checksums(db_path, table, entries):
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for e in entries:
            cur.execute(f"""
                INSERT INTO {table} (uid, relative_path, size, last_modified, checksum, checksum_stale)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(uid, relative_path) DO UPDATE SET
                    size=excluded.size,
                    last_modified=excluded.last_modified,
                    checksum=excluded.checksum,
                    checksum_stale=excluded.checksum_stale
            """, (e['uid'], e['relative_path'], e['size'], e['last_modified'], e.get('checksum'), e.get('checksum_stale', 1)))
        conn.commit()

def test_import_checksums(tmp_path):
    old_db = tmp_path / "old.db"
    new_db = tmp_path / "new.db"
    table = "source_files"
    # Old DB has checksums
    make_db_with_checksums(old_db, table, [
        {'uid': 'vol1', 'relative_path': 'file1.txt', 'size': 100, 'last_modified': 1, 'checksum': 'abc123', 'checksum_stale': 0},
        {'uid': 'vol1', 'relative_path': 'file2.txt', 'size': 200, 'last_modified': 2, 'checksum': 'def456', 'checksum_stale': 0},
    ])
    # New DB has same files but no checksums
    make_db_with_checksums(new_db, table, [
        {'uid': 'vol1', 'relative_path': 'file1.txt', 'size': 100, 'last_modified': 1, 'checksum': None, 'checksum_stale': 1},
        {'uid': 'vol1', 'relative_path': 'file2.txt', 'size': 200, 'last_modified': 2, 'checksum': None, 'checksum_stale': 1},
    ])
    updates = import_checksums_from_old_db(new_db, old_db, table)
    assert updates == 2
    with sqlite3.connect(new_db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT checksum, checksum_stale FROM {table} WHERE uid='vol1' AND relative_path='file1.txt'")
        checksum, stale = cur.fetchone()
        assert checksum == 'abc123'
        assert stale == 0
        cur.execute(f"SELECT checksum, checksum_stale FROM {table} WHERE uid='vol1' AND relative_path='file2.txt'")
        checksum, stale = cur.fetchone()
        assert checksum == 'def456'
        assert stale == 0

def test_import_checksums_to_cache(tmp_path):
    old_db = tmp_path / "old.db"
    new_db = tmp_path / "new.db"
    table = "source_files"
    # Old DB has checksums
    make_db_with_checksums(old_db, table, [
        {'uid': 'vol1', 'relative_path': 'file1.txt', 'size': 100, 'last_modified': 1, 'checksum': 'abc123', 'checksum_stale': 0},
        {'uid': 'vol1', 'relative_path': 'file2.txt', 'size': 200, 'last_modified': 2, 'checksum': 'def456', 'checksum_stale': 0},
    ])
    # New DB has same files but no checksums
    make_db_with_checksums(new_db, table, [
        {'uid': 'vol1', 'relative_path': 'file1.txt', 'size': 100, 'last_modified': 1, 'checksum': None, 'checksum_stale': 1},
        {'uid': 'vol1', 'relative_path': 'file2.txt', 'size': 200, 'last_modified': 2, 'checksum': None, 'checksum_stale': 1},
    ])
    inserts = import_checksums_to_cache(new_db, old_db, table)
    assert inserts == 2
    with sqlite3.connect(new_db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT checksum FROM checksum_cache WHERE uid='vol1' AND relative_path='file1.txt'")
        checksum = cur.fetchone()[0]
        assert checksum == 'abc123'
        cur.execute("SELECT checksum FROM checksum_cache WHERE uid='vol1' AND relative_path='file2.txt'")
        checksum = cur.fetchone()[0]
        assert checksum == 'def456'
