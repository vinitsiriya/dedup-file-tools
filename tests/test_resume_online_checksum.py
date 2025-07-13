import os
import sqlite3
import subprocess
import sys
import pytest
from pathlib import Path
from fs_copy_tool.main import get_db_path_from_job_dir

def run_cli(args, cwd=None):
    cmd = [sys.executable, '-m', 'fs_copy_tool.main'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

def test_file_level_resume_and_online_checksum(tmp_path):
    job_dir = tmp_path / "job"
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    os.makedirs(src_dir)
    os.makedirs(dst_dir)
    (src_dir / "a.txt").write_text("abc")
    (src_dir / "b.txt").write_text("def")
    # 1. Init job directory
    result = run_cli(["init", "--job-dir", str(job_dir)])
    assert result.returncode == 0
    db_path = get_db_path_from_job_dir(job_dir)
    # 2. Analyze
    result = run_cli(["analyze", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 3. Checksum
    result = run_cli(["checksum", "--job-dir", str(job_dir), "--table", "source_files"])
    assert result.returncode == 0
    # 4. Copy (simulate interruption after first file)
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # Remove one file from destination to simulate interruption
    (dst_dir / "b.txt").unlink()
    # 5. Resume copy
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 6. Check that both files exist and contents match
    assert (dst_dir / "a.txt").read_text() == "abc"
    assert (dst_dir / "b.txt").read_text() == "def"
    # 7. Check database for file-level status
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT copy_status FROM source_files WHERE relative_path='a.txt'")
        assert cur.fetchone()[0] == 'done'
        cur.execute("SELECT copy_status FROM source_files WHERE relative_path='b.txt'")
        assert cur.fetchone()[0] == 'done'
