import os
import sqlite3
import tempfile
from fs_copy_tool.db import init_db
from fs_copy_tool.phases.analysis import analyze_volumes
from fs_copy_tool.phases.checksum import update_checksums
from fs_copy_tool.phases.copy import copy_files

def test_db_schema(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        assert 'source_files' in tables
        assert 'destination_files' in tables

def test_end_to_end(tmp_path):
    db_path = tmp_path / "test.db"
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()
    (src_dir / "a.txt").write_text("abc")
    (src_dir / "b.txt").write_text("def")
    init_db(db_path)
    analyze_volumes(db_path, [str(src_dir)], 'source_files')
    analyze_volumes(db_path, [str(dst_dir)], 'destination_files')
    update_checksums(db_path, 'source_files')
    update_checksums(db_path, 'destination_files')
    copy_files(db_path, [str(src_dir)], [str(dst_dir)])
    # After copy, destination should have both files
    assert (dst_dir / "a.txt").exists()
    assert (dst_dir / "b.txt").exists()
