import tempfile
import sqlite3
from pathlib import Path
from dedup_file_tools_fs_copy import main
from dedup_file_tools_fs_copy.utils.uidpath import UidPathUtil
import pytest

def test_import_checksums_from_other_db(tmp_path):

    # Setup: create two job dirs (main and other)
    main_job = tmp_path / "main_job"
    other_job = tmp_path / "other_job"
    src_dir = tmp_path / "src"
    job_name = "testjob"
    main_job.mkdir()
    other_job.mkdir()
    src_dir.mkdir()
    # Create a file in src_dir
    file_path = src_dir / "file1.txt"
    file_path.write_text("imported content")

    # 1. Init both jobs
    args = main.parse_args(["init", "--job-dir", str(main_job), "--job-name", job_name])
    assert main.run_main_command(args) == 0
    args = main.parse_args(["init", "--job-dir", str(other_job), "--job-name", job_name])
    assert main.run_main_command(args) == 0

    # 2. Analyze and checksum in other_job (use source_files table)
    args = main.parse_args(["analyze", "--job-dir", str(other_job), "--job-name", job_name, "--src", str(src_dir)])
    assert main.run_main_command(args) == 0
    args = main.parse_args(["checksum", "--job-dir", str(other_job), "--job-name", job_name, "--table", "source_files"])
    assert main.run_main_command(args) == 0

    # 3. Import checksums from other_job into main_job
    args = main.parse_args(["import-checksums", "--job-dir", str(main_job), "--job-name", job_name, "--other-db", str(other_job / "checksum-cache.db")])
    assert main.run_main_command(args) == 0

    # 4. Validate that checksum_cache in main_job now contains the imported file
    checksum_db_path = main_job / "checksum-cache.db"
    uid_path = UidPathUtil()
    uid_path_obj = uid_path.convert_path(str(file_path))
    uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
    with sqlite3.connect(":memory:") as conn:
        conn.execute(f"ATTACH DATABASE '{checksum_db_path}' AS checksumdb")
        row = conn.execute("SELECT relative_path, checksum FROM checksumdb.checksum_cache WHERE uid=? AND relative_path=?", (uid, rel_path)).fetchone()
        assert row is not None, f"Checksum not imported from other db for uid={uid}, rel_path={rel_path}"
        assert row[0] == rel_path
        assert isinstance(row[1], str) and len(row[1]) > 0

    # 5. Negative test: try importing from a db with no checksum_cache table
    empty_db = tmp_path / "empty.db"
    with sqlite3.connect(empty_db) as conn:
        conn.execute("CREATE TABLE dummy (id INTEGER PRIMARY KEY)")
    args = main.parse_args(["import-checksums", "--job-dir", str(main_job), "--job-name", job_name, "--other-db", str(empty_db)])
    with pytest.raises(SystemExit):
        main.run_main_command(args)
