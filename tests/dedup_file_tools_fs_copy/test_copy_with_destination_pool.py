import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_fs_copy import main

def test_copy_with_destination_pool(tmp_path):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    job_dir = tmp_path / "job"
    job_name = "testjob"
    src_dir.mkdir()
    dst_dir.mkdir()
    job_dir.mkdir()
    # Create files in source
    file1 = src_dir / "file1.txt"
    file2 = src_dir / "file2.txt"
    file1.write_text("foo")
    file2.write_text("bar")
    # Create a duplicate file in destination (should trigger dedup)
    dst_file1 = dst_dir / "file1.txt"
    dst_file1.write_text("foo")
    # 1. Init job dir
    args = main.parse_args(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    assert main.run_main_command(args) == 0
    # 2. Analyze source and destination
    args = main.parse_args(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--src", str(src_dir), "--dst", str(dst_dir)])
    assert main.run_main_command(args) == 0
    # 3. Checksum phase for source and destination
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--job-name", job_name, "--table", "source_files"])
    assert main.run_main_command(args) == 0
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--job-name", job_name, "--table", "destination_files"])
    assert main.run_main_command(args) == 0
    # 4. Add to destination pool
    args = main.parse_args(["add-to-destination-index-pool", "--job-dir", str(job_dir), "--job-name", job_name, "--dst", str(dst_dir)])
    assert main.run_main_command(args) == 0
    # 5. Copy with pool deduplication
    args = main.parse_args(["copy", "--job-dir", str(job_dir), "--job-name", job_name, "--src", str(src_dir), "--dst", str(dst_dir)])
    assert main.run_main_command(args) == 0
    # file1.txt should be skipped, file2.txt should be copied
    found1 = list(dst_dir.rglob("file1.txt"))
    found2 = list(dst_dir.rglob("file2.txt"))
    assert found1 and found1[0].read_text() == "foo"
    assert found2 and found2[0].read_text() == "bar"
    # Check DB for status
    db_path = job_dir / f"{job_name}.db"
    with sqlite3.connect(db_path) as conn:
        row1 = conn.execute("""
            SELECT cs.status FROM copy_status cs JOIN source_files s ON cs.uid = s.uid AND cs.relative_path = s.relative_path WHERE s.relative_path LIKE ?
        """, ("%file1.txt",)).fetchone()
        row2 = conn.execute("""
            SELECT cs.status FROM copy_status cs JOIN source_files s ON cs.uid = s.uid AND cs.relative_path = s.relative_path WHERE s.relative_path LIKE ?
        """, ("%file2.txt",)).fetchone()
        assert row1 and row1[0] == 'done'
        assert row2 and row2[0] == 'done'
