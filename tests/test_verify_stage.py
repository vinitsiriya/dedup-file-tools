import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import pytest

def test_shallow_and_deep_verify_stage(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    job = tmp_path / "job"
    src.mkdir()
    dst.mkdir()
    job.mkdir()
    # Create a file in source
    file_path = src / "file1.txt"
    file_path.write_text("verify me!")
    # Init, analyze, checksum, copy
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "init", "--job-dir", str(job)], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "analyze", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "destination_files"], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "copy", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], check=True)
    # Shallow verify
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "verify", "--job-dir", str(job), "--src", str(src), "--dst", str(dst), "--stage", "shallow"], check=True)
    db_path = job / "copytool.db"
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT \"exists\", size_matched, last_modified_matched, verify_status, verify_error FROM verification_shallow_results WHERE relative_path=? ORDER BY timestamp DESC LIMIT 1", ("file1.txt",))
        row = cur.fetchone()
        assert row is not None, "No shallow verification entry for file1.txt"
        assert row[0] == 1, "File should exist at destination"
        assert row[1] == 1, "Size should match"
        assert row[2] == 1, "Last modified should match"
        assert row[3] == "ok", f"Expected verify_status 'ok', got {row[3]}"
        assert row[4] is None, f"Expected no verify_error, got {row[4]}"
    # Deep verify
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "verify", "--job-dir", str(job), "--src", str(src), "--dst", str(dst), "--stage", "deep"], check=True)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT checksum_matched, verify_status, verify_error FROM verification_deep_results WHERE relative_path=? ORDER BY timestamp DESC LIMIT 1", ("file1.txt",))
        row = cur.fetchone()
        assert row is not None, "No deep verification entry for file1.txt"
        assert row[0] == 1, "Checksum should match"
        assert row[1] == "ok", f"Expected verify_status 'ok', got {row[1]}"
        assert row[2] is None, f"Expected no verify_error, got {row[2]}"

def test_deep_verify_detects_corruption(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    job = tmp_path / "job"
    src.mkdir()
    dst.mkdir()
    job.mkdir()
    file_path = src / "file1.txt"
    file_path.write_text("verify me!")
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "init", "--job-dir", str(job)], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "analyze", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "destination_files"], check=True)
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "copy", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], check=True)
    # Corrupt the destination file
    (dst / "file1.txt").write_text("corrupted!")
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "verify", "--job-dir", str(job), "--src", str(src), "--dst", str(dst), "--stage", "deep"], check=True)
    db_path = job / "copytool.db"
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT checksum_matched, verify_status, verify_error FROM verification_deep_results WHERE relative_path=? ORDER BY timestamp DESC LIMIT 1", ("file1.txt",))
        row = cur.fetchone()
        assert row is not None, "No deep verification entry for file1.txt"
        assert row[0] == 0, "Checksum should not match after corruption"
        assert row[1] == "failed", f"Expected verify_status 'failed', got {row[1]}"
        assert row[2] == "Checksum mismatch", f"Expected verify_error 'Checksum mismatch', got {row[2]}"
