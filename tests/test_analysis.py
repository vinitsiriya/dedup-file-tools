import os
import sqlite3
import tempfile
import pytest
from pathlib import Path
from dedup_file_tools_fs_copy.phases.analysis import persist_file_metadata, scan_files_on_volume, analyze_volumes
from dedup_file_tools_fs_copy.utils.uidpath import UidPathUtil

def setup_test_db(tmp_path, table):
    db_path = tmp_path / "test_analysis.db"
    conn = sqlite3.connect(db_path)
    conn.execute(f"""
        CREATE TABLE {table} (
            uid TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            size INTEGER,
            last_modified INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    conn.commit()
    conn.close()
    return str(db_path)

def test_persist_file_metadata_insert_and_update(tmp_path):
    table = "test_files"
    db_path = setup_test_db(tmp_path, table)
    file_info = {
        'uid': 'testuid',
        'relative_path': 'file1.txt',
        'size': 123,
        'last_modified': 1111
    }
    persist_file_metadata(db_path, table, file_info)
    # Update
    file_info['size'] = 456
    file_info['last_modified'] = 2222
    persist_file_metadata(db_path, table, file_info)
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(f"SELECT size, last_modified FROM {table} WHERE uid=? AND relative_path=?", ('testuid', 'file1.txt')).fetchone()
        assert row == (456, 2222)

def test_scan_files_on_volume(tmp_path):
    uid_path = UidPathUtil()
    d = tmp_path / "scanme"
    d.mkdir()
    (d / "a.txt").write_text("a")
    (d / "b.txt").write_text("b")
    files = list(scan_files_on_volume(str(d), uid_path))
    rels = {f['relative_path'] for f in files}
    # Compare basenames to expected filenames
    assert {os.path.basename(r) for r in rels} == {"a.txt", "b.txt"}
    for f in files:
        # Accept any non-empty UID (int or str), just check it's present
        assert f['uid'] is not None
        assert f['size'] > 0
        assert isinstance(f['last_modified'], int)

def test_analyze_volumes(tmp_path):
    table = "test_files"
    db_path = setup_test_db(tmp_path, table)
    d = tmp_path / "analyzeme"
    d.mkdir()
    (d / "x.txt").write_text("x")
    (d / "y.txt").write_text("y")
    analyze_volumes(db_path, [str(d)], table)
    with sqlite3.connect(db_path) as conn:
        rows = list(conn.execute(f"SELECT relative_path FROM {table}"))
        rels = {r[0] for r in rows}
        # Compare basenames to expected filenames
        assert {os.path.basename(r) for r in rels} == {"x.txt", "y.txt"}
