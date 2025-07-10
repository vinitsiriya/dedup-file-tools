import os
import sqlite3
import subprocess
import sys
import pytest
from fs_copy_tool.main import init_job_dir, get_db_path_from_job_dir

def run_cli(args, cwd=None):
    cmd = [sys.executable, '-m', 'fs_copy_tool.main'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

def test_cli_resume_status_log(tmp_path):
    job_dir = tmp_path / "job"
    os.makedirs(job_dir)
    db_path = get_db_path_from_job_dir(job_dir)
    init_job_dir(job_dir)
    # Insert a pending file
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO source_files (uid, relative_path, size, last_modified, checksum, checksum_stale, copy_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("vol1", "file1.txt", 100, 1, "abc123", 0, "pending"))
        conn.commit()
    # Test status command
    result = run_cli(["status", "--job-dir", str(job_dir)])
    assert "Pending" in result.stdout or "pending" in result.stdout
    # Test log command
    result = run_cli(["log", "--job-dir", str(job_dir)])
    assert "file1.txt" in result.stdout
    # Test resume command (should not error)
    result = run_cli(["resume", "--job-dir", str(job_dir), "--src", str(tmp_path), "--dst", str(tmp_path)])
    assert result.returncode == 0
