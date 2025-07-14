import os
import shutil
import subprocess
import sqlite3
from pathlib import Path

def test_incremental_checksums(tmp_path):
    """
    E2E: Handles cases where some checksums are already loaded.
    - Step 1: Create src with fileA, fileB. Run checksum (fileA, fileB).
    - Step 2: Add fileC, modify fileA, delete fileB. Run checksum again.
    - Step 3: Only fileA (changed) and fileC (new) should be rechecksummed/copied.
    - Step 4: fileB's checksum may remain in DB, but file should not be copied.
    """
    workspace = tmp_path / "manual_tests" / "incremental_checksums"
    src = workspace / "src"
    dst = workspace / "dst"
    job = workspace / "job"
    src.mkdir(parents=True)
    dst.mkdir()
    # Step 1: Create initial files
    (src / "fileA.txt").write_text("A1")
    (src / "fileB.txt").write_text("B1")
    python = str(Path(".venv/Scripts/python.exe")) if Path(".venv/Scripts/python.exe").exists() else "python"
    subprocess.run([python, "fs_copy_tool/main.py", "init", "--job-dir", str(job)], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "add-source", "--job-dir", str(job), "--src", str(src)], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    # Step 2: Add fileC, modify fileA, delete fileB
    (src / "fileA.txt").write_text("A2")  # modify
    (src / "fileC.txt").write_text("C1")  # new
    (src / "fileB.txt").unlink()          # delete
    subprocess.run([python, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    # Step 3: Run copy
    subprocess.run([python, "fs_copy_tool/main.py", "copy", "--job-dir", str(job), "--dst", str(dst)], check=True)
    # Step 4: Assert only on file system, not DB
    assert (dst / str(src / "fileA.txt")).read_text() == "A2"
    assert (dst / str(src / "fileC.txt")).read_text() == "C1"
    assert not (dst / str(src / "fileB.txt")).exists()
