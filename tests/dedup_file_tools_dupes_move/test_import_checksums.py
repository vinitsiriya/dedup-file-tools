import os
import sqlite3
import tempfile
import shutil
import pytest
from dedup_file_tools_dupes_move.handlers import handle_import_checksums
from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir, get_checksum_db_path

def create_test_db_with_checksums(db_path, checksums):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS checksum_cache (
            uid TEXT, relative_path TEXT, size INTEGER, last_modified INTEGER, checksum TEXT,
            imported_at INTEGER, last_validated INTEGER, is_valid INTEGER
        )
    """)
    cur.executemany("""
        INSERT INTO checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, checksums)
    conn.commit()
    conn.close()

def test_handle_import_checksums(tmp_path):
    # Setup source DB with checksums
    src_db = tmp_path / "src_checksums.db"
    checksums = [
        (f"uid{i}", f"file{i}.txt", 100+i, 1234567890+i, f"abc{i}", 1111+i, 2222+i, 1)
        for i in range(10)
    ]
    create_test_db_with_checksums(str(src_db), checksums)

    # Setup dest job dir and DB
    job_dir = tmp_path / "job"
    job_dir.mkdir()
    job_name = "testjob"
    dest_db = get_db_path_from_job_dir(str(job_dir), job_name)
    checksum_db = get_checksum_db_path(str(job_dir))
    # Create empty dest DB and checksum DB
    sqlite3.connect(dest_db).close()
    sqlite3.connect(checksum_db).close()

    # Run import
    handle_import_checksums(str(job_dir), job_name, str(src_db))

    # Validate import
    conn = sqlite3.connect(checksum_db)
    cur = conn.cursor()
    cur.execute("SELECT uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid FROM checksum_cache")
    imported = cur.fetchall()
    conn.close()
    assert len(imported) == len(checksums)
    for row in imported:
        assert row in checksums

if __name__ == "__main__":
    pytest.main([__file__])
