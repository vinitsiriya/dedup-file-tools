import os
import subprocess
import sys
from pathlib import Path
import pytest

def run_cli(args, cwd=None):
    cmd = [sys.executable, '-m', 'fs_copy_tool.main'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result

def test_e2e_resume_file_level(tmp_path):
    job_dir = tmp_path / "job"
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    os.makedirs(src_dir)
    os.makedirs(dst_dir)
    (src_dir / "file1.txt").write_text("hello world")
    (src_dir / "file2.txt").write_text("goodbye world")
    # 1. Init job directory
    result = run_cli(["init", "--job-dir", str(job_dir)])
    assert result.returncode == 0
    # 2. Analyze
    result = run_cli(["analyze", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 3. Checksum
    result = run_cli(["checksum", "--job-dir", str(job_dir), "--table", "source_files"])
    assert result.returncode == 0
    # 4. Copy all files
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 5. Simulate interruption: delete one file from destination
    (dst_dir / "file2.txt").unlink()
    # 6. Resume copy
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 7. Check that both files exist and contents match
    assert (dst_dir / "file1.txt").read_text() == "hello world"
    assert (dst_dir / "file2.txt").read_text() == "goodbye world"
