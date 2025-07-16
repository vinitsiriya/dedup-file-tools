import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from fs_copy_tool import main

def test_cli_workflow_copy(tmp_path):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    job_dir = tmp_path / "job"
    src_dir.mkdir()
    dst_dir.mkdir()
    job_dir.mkdir()
    # Create multiple files to test threading
    file_paths = [src_dir / f"file{i}.txt" for i in range(5)]
    for i, file_path in enumerate(file_paths):
        file_path.write_text(f"hello world {i}")

    # 1. Init job dir
    args = main.parse_args(["init", "--job-dir", str(job_dir)])
    assert main.run_main_command(args) == 0

    # 2. Analyze source
    args = main.parse_args(["analyze", "--job-dir", str(job_dir), "--src", str(src_dir)])
    assert main.run_main_command(args) == 0

    # 3. Checksum phase
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--table", "source_files"])
    assert main.run_main_command(args) == 0

    # 4. Copy phase (use more threads)
    args = main.parse_args(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir), "--threads", "3"])
    assert main.run_main_command(args) == 0

    # Assert all files exist in destination
    for i in range(5):
        found = list(dst_dir.rglob(f"file{i}.txt"))
        print(f"[DEBUG] dst_dir contents for file{i}.txt: {[str(p) for p in dst_dir.rglob('*')]}" )
        assert found, f"file{i}.txt not found in {dst_dir}"
        assert found[0].read_text() == f"hello world {i}"

    # Optionally, check DB for status after copy
    db_path = job_dir / "copytool.db"
    with sqlite3.connect(db_path) as conn:
        for i in range(5):
            row = conn.execute("SELECT copy_status FROM source_files WHERE relative_path LIKE ?", (f"%file{i}.txt",)).fetchone()
            print(f"[DEBUG] DB copy_status for file{i}.txt: {row}")
            assert row and row[0] == 'done'
    print("[INFO] Copy phase and DB status checks passed.")
