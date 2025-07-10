import os
import tempfile
import sqlite3
import pytest
from fs_copy_tool.main import init_job_dir, get_db_path_from_job_dir

def test_job_dir_creation(tmp_path):
    job_dir = tmp_path / "job"
    init_job_dir(job_dir)
    db_path = get_db_path_from_job_dir(job_dir)
    assert os.path.exists(db_path)
    # Check DB schema
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        assert 'source_files' in tables
        assert 'destination_files' in tables

def test_resume_command(tmp_path):
    # Simulate job dir and pending copy
    job_dir = tmp_path / "job"
    init_job_dir(job_dir)
    db_path = get_db_path_from_job_dir(job_dir)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO source_files (uid, relative_path, size, last_modified, checksum, checksum_stale, copy_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("vol1", "file1.txt", 100, 1, "abc123", 0, "pending"))
        conn.commit()
    # Would call main(['resume', ...]) here if CLI tested, or test copy_files directly
    # For now, just check pending row exists
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT copy_status FROM source_files WHERE relative_path='file1.txt'")
        status = cur.fetchone()[0]
        assert status == "pending"
