import os
import sqlite3
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import pytest

def create_old_db(db_path, uid, rel_path, size, last_modified, checksum):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS source_files (
                uid TEXT, relative_path TEXT, last_modified INTEGER, size INTEGER, checksum TEXT, checksum_stale INTEGER, copy_status TEXT, last_copy_attempt INTEGER, error_message TEXT, PRIMARY KEY (uid, relative_path)
            )
        """)
        cur.execute("""
            INSERT INTO source_files (uid, relative_path, last_modified, size, checksum, checksum_stale, copy_status, last_copy_attempt, error_message)
            VALUES (?, ?, ?, ?, ?, 0, 'done', 0, NULL)
        """, (uid, rel_path, last_modified, size, checksum))
        conn.commit()

def test_import_checksums_e2e(tmp_path):
    # Setup: create a file and compute its checksum
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    job = tmp_path / "job"
    old_job = tmp_path / "old_job"
    src.mkdir()
    dst.mkdir()
    job.mkdir()
    old_job.mkdir()
    file_path = src / "file1.txt"
    file_path.write_text("imported content")
    # Compute checksum
    import hashlib
    checksum = hashlib.sha256(b"imported content").hexdigest()
    # Init new job
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "init", "--job-dir", str(job)], check=True)
    # Analyze
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "analyze", "--job-dir", str(job), "--src", str(src), "--dst", str(dst)], check=True)
    # Get actual uid, rel_path, size, last_modified from new db
    db_path = job / "copytool.db"
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM source_files")
        all_rows = cur.fetchall()
        print("source_files rows after analyze:", all_rows)
        # Find the row for our file by matching on the filename
        for row in all_rows:
            if row[1].endswith("file1.txt"):
                uid, rel_path, size, last_modified = row
                break
        else:
            assert False, f"No entry found for file1.txt in source_files: {all_rows}"
    # Create old db with matching metadata
    old_db_path = old_job / "copytool.db"
    create_old_db(old_db_path, uid, rel_path, size, last_modified, checksum)
    # Import checksums
    subprocess.run([sys.executable, "fs_copy_tool/main.py", "import-checksums", "--job-dir", str(job), "--old-db", str(old_db_path), "--table", "source_files"], check=True)
    # Check that checksum is present in new db
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT checksum FROM source_files WHERE relative_path=?", (rel_path,))
        row = cur.fetchone()
        assert row is not None, f"No entry found for imported file with rel_path={rel_path}"
        assert row[0] == checksum, f"Checksum mismatch: expected {checksum}, got {row[0]}"
