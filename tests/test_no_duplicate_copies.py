import os
import shutil
import sqlite3
from pathlib import Path
from fs_copy_tool.main import main as fs_copy_tool_main
import pytest

def setup_test_env(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    job = tmp_path / "job"
    src.mkdir()
    dst.mkdir()
    job.mkdir()
    # Create two files with the same content but different names/paths
    (src / "file1.txt").write_text("duplicate content")
    (src / "file2.txt").write_text("duplicate content")
    return src, dst, job

def run_cli(args, tmp_path):
    # Simulate CLI call
    import sys
    old_argv = sys.argv
    sys.argv = ["fs_copy_tool"] + args
    try:
        fs_copy_tool_main()
    finally:
        sys.argv = old_argv

def test_no_duplicate_copies(tmp_path):
    src, dst, job = setup_test_env(tmp_path)
    db_path = job / "copytool.db"
    # Init
    run_cli(["init", "--job-dir", str(job)], tmp_path)
    # Analyze
    run_cli(["analyze", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], tmp_path)
    # Checksum
    run_cli(["checksum", "--job-dir", str(job), "--table", "source_files"], tmp_path)
    run_cli(["checksum", "--job-dir", str(job), "--table", "destination_files"], tmp_path)
    # Copy
    run_cli(["copy", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], tmp_path)
    # Check destination: only one file with the content should exist
    files = list(dst.rglob("*"))
    file_contents = [f.read_text() for f in files if f.is_file()]
    assert file_contents.count("duplicate content") == 1, f"Expected only one copy, found {file_contents.count('duplicate content')}"
    # Check database: only one destination file with that checksum
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM destination_files WHERE checksum = (SELECT checksum FROM destination_files LIMIT 1)")
        count = cur.fetchone()[0]
        assert count == 1, f"Expected only one db entry for the checksum, found {count}"
