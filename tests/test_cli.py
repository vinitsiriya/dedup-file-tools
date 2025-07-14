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

def test_add_file_and_list_files(tmp_path):
    job_dir = tmp_path / "job2"
    os.makedirs(job_dir)
    test_file = tmp_path / "f.txt"
    test_file.write_text("abc")
    run_cli(["init", "--job-dir", str(job_dir)])
    result = run_cli(["add-file", "--job-dir", str(job_dir), "--file", str(test_file)])
    # Accept output in either stdout or stderr
    output = result.stdout + result.stderr
    assert "Added file" in output
    result = run_cli(["list-files", "--job-dir", str(job_dir)])
    assert "f.txt" in result.stdout or "f.txt" in result.stderr
    result = run_cli(["remove-file", "--job-dir", str(job_dir), "--file", str(test_file)])
    output = result.stdout + result.stderr
    assert "Removed file" in output
    result = run_cli(["list-files", "--job-dir", str(job_dir)])
    assert "f.txt" not in result.stdout and "f.txt" not in result.stderr

def test_cli_init(tmp_path):
    job_dir = tmp_path / "job3"
    os.makedirs(job_dir)
    result = run_cli(["init", "--job-dir", str(job_dir)])
    assert result.returncode == 0
    assert os.path.exists(get_db_path_from_job_dir(job_dir))

def test_cli_add_file(tmp_path):
    job_dir = tmp_path / "job4"
    os.makedirs(job_dir)
    db_path = get_db_path_from_job_dir(job_dir)
    init_job_dir(job_dir)
    test_file = tmp_path / "file_to_add.txt"
    test_file.write_text("This is a test file.")
    result = run_cli(["add-file", "--job-dir", str(job_dir), "--file", str(test_file)])
    assert result.returncode == 0
    # Use the parent directory as UID, matching CLI logic
    uid = str(test_file.parent)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT relative_path FROM source_files WHERE uid=?", (uid,))
        files = cur.fetchall()
        assert len(files) == 1
        assert files[0][0] == "file_to_add.txt"

def test_cli_remove_file(tmp_path):
    job_dir = tmp_path / "job5"
    os.makedirs(job_dir)
    db_path = get_db_path_from_job_dir(job_dir)
    init_job_dir(job_dir)
    # Add a file first
    test_file = tmp_path / "file_to_remove.txt"
    test_file.write_text("This file will be removed.")
    run_cli(["add-file", "--job-dir", str(job_dir), "--file", str(test_file)])
    # Use the parent directory as UID, matching CLI logic
    uid = str(test_file.parent)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT relative_path FROM source_files WHERE uid=?", (uid,))
        files = cur.fetchall()
        assert len(files) == 1
        assert files[0][0] == "file_to_remove.txt"
    # Now remove the file
    result = run_cli(["remove-file", "--job-dir", str(job_dir), "--file", str(test_file)])
    assert result.returncode == 0
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT relative_path FROM source_files WHERE uid=?", (uid,))
        files = cur.fetchall()
        assert len(files) == 0
