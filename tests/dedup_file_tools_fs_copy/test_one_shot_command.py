
import os
import pytest
from dedup_file_tools_fs_copy import main

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
        "one-shot",
        "--job-dir", str(job_dir),
        "--job-name", "testjob",
        "--src", str(src_dir),
        "--dst", str(dst_dir)
    ]
    parsed_args = main.parse_args(args)
    rc = main.run_main_command(parsed_args)
    assert rc == 0
    found = list(dst_dir.rglob("file1.txt"))
    assert found, f"file1.txt not found in {dst_dir}"
    with open(found[0], "r") as f:
        content = f.read()
    assert content == "hello world"
    summary_report = job_dir / "summary_report.csv"
    assert summary_report.exists(), f"Expected summary report at {summary_report}"

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
        "one-shot",
        "--job-dir", str(job_dir),
        "--job-name", "testjob2",
        "--src", str(src_dir),
        "--dst", str(dst_dir),
        "--threads", "2",
        "--no-progress",
        "--log-level", "DEBUG"
    ]
    parsed_args = main.parse_args(args)
    rc = main.run_main_command(parsed_args)
    assert rc == 0
    found = list(dst_dir.rglob("file2.txt"))
    assert found, f"file2.txt not found in {dst_dir}"
    with open(found[0], "r") as f:
        content = f.read()
    assert content == "test file"
    summary_report = job_dir / "summary_report.csv"
    assert summary_report.exists(), f"Expected summary report at {summary_report}"
