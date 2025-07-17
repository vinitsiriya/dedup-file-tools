import sqlite3
from pathlib import Path
from dedup_file_tools_fs_copy import main
from dedup_file_tools_fs_copy.utils.uidpath import UidPathUtil
import pytest

def test_e2e_import_checksums(tmp_path):
    """
    E2E: Simulate two jobs, generate checksums in one, import into another, verify correctness.
    """
    # Setup directories
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "a.txt").write_text("aaa")
    (src_dir / "b.txt").write_text("bbb")

    # Create two job dirs
    job1 = tmp_path / "job1"
    job2 = tmp_path / "job2"
    job1.mkdir()
    job2.mkdir()

    # Job1: init, analyze, checksum
    args = main.parse_args(["init", "--job-dir", str(job1)])
    assert main.run_main_command(args) == 0
    args = main.parse_args(["analyze", "--job-dir", str(job1), "--src", str(src_dir)])
    assert main.run_main_command(args) == 0
    args = main.parse_args(["checksum", "--job-dir", str(job1), "--table", "source_files"])
    assert main.run_main_command(args) == 0

    # Job2: init
    args = main.parse_args(["init", "--job-dir", str(job2)])
    assert main.run_main_command(args) == 0

    # Import checksums from job1 to job2
    args = main.parse_args(["import-checksums", "--job-dir", str(job2), "--other-db", str(job1 / "copytool.db")])
    assert main.run_main_command(args) == 0

    # Validate both files imported in job2's checksum_cache
    db_path = job2 / "copytool.db"
    uid_path = UidPathUtil()
    for fname in ["a.txt", "b.txt"]:
        fpath = src_dir / fname
        uid, rel_path = uid_path.convert_path(str(fpath))
        with sqlite3.connect(db_path) as conn:
            row = conn.execute("SELECT checksum FROM checksum_cache WHERE uid=? AND relative_path=?", (uid, rel_path)).fetchone()
            assert row is not None, f"{fname} not imported"
            assert isinstance(row[0], str) and len(row[0]) > 0

    # Negative: import from a db with no checksum_cache
    empty_db = tmp_path / "empty.db"
    with sqlite3.connect(empty_db) as conn:
        conn.execute("CREATE TABLE dummy (id INTEGER PRIMARY KEY)")
    args = main.parse_args(["import-checksums", "--job-dir", str(job2), "--other-db", str(empty_db)])
    with pytest.raises(SystemExit):
        main.run_main_command(args)
