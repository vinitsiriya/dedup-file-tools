import subprocess
import os
import tempfile
import shutil
import pytest

def run_one_shot_command(args):
    venv_python = os.path.join(os.path.dirname(__file__), '..', '.venv', 'Scripts', 'python.exe')
    venv_python = os.path.abspath(venv_python)
    cmd = [venv_python, "-m", "fs_copy_tool.main", "one-shot"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_one_shot_minimal(tmp_path):
    job_dir = tmp_path / "job"
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    os.makedirs(job_dir)
    os.makedirs(src_dir)
    os.makedirs(dst_dir)
    # Create a dummy file in src
    with open(src_dir / "file1.txt", "w") as f:
        f.write("hello world")
    args = [
        "--job-dir", str(job_dir),
        "--job-name", "testjob",
        "--src", str(src_dir),
        "--dst", str(dst_dir)
    ]
    result = run_one_shot_command(args)
    assert result.returncode == 0
    assert "Initialized job directory" in result.stdout or "Initialized job directory" in result.stderr
    assert "Added" in result.stdout or "Added" in result.stderr
    assert "Done" in result.stdout or "Done" in result.stderr

def test_one_shot_with_options(tmp_path):
    job_dir = tmp_path / "job2"
    src_dir = tmp_path / "src2"
    dst_dir = tmp_path / "dst2"
    os.makedirs(job_dir)
    os.makedirs(src_dir)
    os.makedirs(dst_dir)
    with open(src_dir / "file2.txt", "w") as f:
        f.write("test file")
    args = [
        "--job-dir", str(job_dir),
        "--job-name", "testjob2",
        "--src", str(src_dir),
        "--dst", str(dst_dir),
        "--threads", "2",
        "--no-progress",
        "--log-level", "DEBUG"
    ]
    result = run_one_shot_command(args)
    assert result.returncode == 0
    assert "DEBUG" in result.stdout or "DEBUG" in result.stderr
    assert "Added" in result.stdout or "Added" in result.stderr
    assert "Done" in result.stdout or "Done" in result.stderr
