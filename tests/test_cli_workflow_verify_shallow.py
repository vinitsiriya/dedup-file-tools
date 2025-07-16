import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from fs_copy_tool import main

def test_cli_workflow_verify_shallow(tmp_path):

    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    job_dir = tmp_path / "job"
    job_name = "testjob"
    src_dir.mkdir()
    dst_dir.mkdir()
    job_dir.mkdir()
    # Create multiple files to test threading
    file_paths = [src_dir / f"file{i}.txt" for i in range(5)]
    for i, file_path in enumerate(file_paths):
        file_path.write_text(f"hello world {i}")

    # 1. Init job dir
    args = main.parse_args(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    assert main.run_main_command(args) == 0

    # 2. Analyze source
    args = main.parse_args(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--src", str(src_dir)])
    assert main.run_main_command(args) == 0

    # 3. Checksum phase
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--job-name", job_name, "--table", "source_files"])
    assert main.run_main_command(args) == 0

    # 4. Copy phase (use more threads)
    args = main.parse_args(["copy", "--job-dir", str(job_dir), "--job-name", job_name, "--src", str(src_dir), "--dst", str(dst_dir), "--threads", "3"])
    assert main.run_main_command(args) == 0

    # 5. Shallow verify phase
    args = main.parse_args(["verify", "--job-dir", str(job_dir), "--job-name", job_name])
    assert main.run_main_command(args) == 0

    # Check DB for shallow verify results
    db_path = job_dir / f"{job_name}.db"
    with sqlite3.connect(db_path) as conn:
        for i in range(5):
            row = conn.execute(
                "SELECT verify_status FROM verification_shallow_results WHERE relative_path LIKE ? ORDER BY timestamp DESC LIMIT 1",
                (f"%file{i}.txt",)
            ).fetchone()
            print(f"[DEBUG] DB shallow verify_status for file{i}.txt: {row}")
            assert row and row[0] == 'ok'
    print("[INFO] Shallow verify phase and DB status checks passed.")
