import os
import sqlite3
import tempfile
from pathlib import Path
import pytest
from dedup_file_tools_dupes_move.phases.analysis import find_and_queue_duplicates
from dedup_file_tools_commons.utils.uidpath import UidPathUtil

def setup_test_db(tmp_path):
    db_path = tmp_path / "test_dupes_move.db"
    conn = sqlite3.connect(db_path)
    # Create dedup_files_pool
    conn.execute("""
        CREATE TABLE dedup_files_pool (
            uid TEXT,
            relative_path TEXT,
            size INTEGER,
            last_modified INTEGER,
            checksum TEXT,
            scanned_at INTEGER,
            pool_base_path TEXT,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    # Create dedup_move_plan
    conn.execute("""
        CREATE TABLE dedup_move_plan (
            uid TEXT,
            relative_path TEXT,
            checksum TEXT,
            move_to_uid TEXT,
            move_to_rel_path TEXT,
            status TEXT,
            error_message TEXT,
            planned_at INTEGER,
            moved_at INTEGER,
            updated_at INTEGER,
            is_keeper INTEGER DEFAULT 0,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    conn.commit()
    conn.close()
    return str(db_path)

def test_find_and_queue_duplicates(tmp_path):
    # Setup test files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "a.txt").write_text("hello")
    (src_dir / "b.txt").write_text("hello")  # duplicate content
    (src_dir / "c.txt").write_text("unique")
    db_path = setup_test_db(tmp_path)
    # Run analysis
    find_and_queue_duplicates(db_path, str(src_dir), threads=1)
    # Check dedup_files_pool
    with sqlite3.connect(db_path) as conn:
        rows = list(conn.execute("SELECT relative_path, checksum FROM dedup_files_pool"))
        rels = {r[0] for r in rows}
        assert {os.path.basename(r) for r in rels} == {"a.txt", "b.txt", "c.txt"}
        # There should be at least one duplicate checksum
        checksums = [r[1] for r in rows]
        assert any(checksums.count(chk) > 1 for chk in checksums)
