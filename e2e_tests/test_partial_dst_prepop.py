import os
import shutil
import subprocess
from pathlib import Path


def test_partial_dst_prepop(tmp_path):
    """
    E2E test: Partial destination prepopulation scenario.
    - Source: fileA, fileB, fileC, fileD
    - Destination prepopulated with fileA, fileC
    - After copy: fileB, fileD should be copied; fileA, fileC should remain unchanged
    - (Current tool copies to dst/<full_source_path>)
    """
    workspace = tmp_path / "manual_tests" / "partial_dst_prepop"
    src = workspace / "src"
    dst = workspace / "dst"
    job = workspace / "job"
    src.mkdir(parents=True)
    dst.mkdir()
    # Create source files
    (src / "fileA.txt").write_text("This is file A")
    (src / "fileB.txt").write_text("This is file B")
    (src / "fileC.txt").write_text("This is file C")
    (src / "fileD.txt").write_text("This is file D")
    # Prepopulate destination
    shutil.copy(src / "fileA.txt", dst / "fileA.txt")
    shutil.copy(src / "fileC.txt", dst / "fileC.txt")
    # Run workflow
    python = str(Path(".venv/Scripts/python.exe")) if Path(".venv/Scripts/python.exe").exists() else "python"
    subprocess.run([python, "dedup_file_tools_fs_copy/main.py", "init", "--job-dir", str(job)], check=True)
    subprocess.run([python, "dedup_file_tools_fs_copy/main.py", "add-source", "--job-dir", str(job), "--src", str(src)], check=True)
    subprocess.run([python, "dedup_file_tools_fs_copy/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    subprocess.run([python, "dedup_file_tools_fs_copy/main.py", "checksum", "--job-dir", str(job), "--table", "destination_files"], check=True)
    subprocess.run([python, "dedup_file_tools_fs_copy/main.py", "copy", "--job-dir", str(job), "--dst", str(dst)], check=True)
    # Assert: files are copied to dst/<full_source_path>
    assert (dst / str(src / "fileA.txt")).read_text() == "This is file A"
    assert (dst / str(src / "fileC.txt")).read_text() == "This is file C"
    assert (dst / str(src / "fileB.txt")).read_text() == "This is file B"
    assert (dst / str(src / "fileD.txt")).read_text() == "This is file D"
