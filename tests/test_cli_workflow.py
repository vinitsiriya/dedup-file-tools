import os
import sqlite3
import subprocess
import sys
import pytest
from fs_copy_tool.main import get_db_path_from_job_dir

def run_cli(args, cwd=None):
    cmd = [sys.executable, '-m', 'fs_copy_tool.main'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

def test_cli_full_workflow(tmp_path):
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
    assert os.path.exists(db_path)
    # 2. Analyze
    result = run_cli(["analyze", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 3. Checksum
    result = run_cli(["checksum", "--job-dir", str(job_dir), "--table", "source_files"])
    assert result.returncode == 0
    result = run_cli(["checksum", "--job-dir", str(job_dir), "--table", "destination_files"])
    assert result.returncode == 0
    # 4. Copy
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 5. Status
    result = run_cli(["status", "--job-dir", str(job_dir)])
    assert "Done" in result.stdout or "done" in result.stdout
    # 6. Log
    result = run_cli(["log", "--job-dir", str(job_dir)])
    assert "a.txt" in result.stdout and "b.txt" in result.stdout
    # 7. Resume (should be a no-op if all done)
    result = run_cli(["resume", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 8. Files should exist in destination
    assert (dst_dir / "a.txt").exists()
    assert (dst_dir / "b.txt").exists()
