import os
import subprocess
import sys
from pathlib import Path
import pytest

def run_cli(args, cwd=None):
    cmd = [sys.executable, '-m', 'fs_copy_tool.main'] + args
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    print(f"[CLI STDOUT] {' '.join(cmd)}\n{result.stdout}")
    print(f"[CLI STDERR] {' '.join(cmd)}\n{result.stderr}")
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
    # 2. Add files using new CLI
    result = run_cli(["add-source", "--job-dir", str(job_dir), "--src", str(src_dir)])
    assert "Added" in result.stdout
    # 3. Analyze destination only
    result = run_cli(["analyze", "--job-dir", str(job_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 4. Checksum
    result = run_cli(["checksum", "--job-dir", str(job_dir), "--table", "source_files"])
    assert result.returncode == 0
    # 5. Copy all files
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 6. Simulate interruption: delete one file from destination
    (dst_dir / "file2.txt").unlink()
    # 7. Resume copy
    result = run_cli(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert result.returncode == 0
    # 8. Check that both files exist and contents match
    print("[TEST DEBUG] dst_dir contents:", list(dst_dir.iterdir()))
    print("[TEST DEBUG] CLI STDOUT (resume copy):\n", result.stdout)
    print("[TEST DEBUG] CLI STDERR (resume copy):\n", result.stderr)
    assert (dst_dir / "file1.txt").read_text() == "hello world"
    assert (dst_dir / "file2.txt").read_text() == "goodbye world"
