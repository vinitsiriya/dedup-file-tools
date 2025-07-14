import os
import shutil
import subprocess
from pathlib import Path

def test_deduplication(tmp_path):
    """
    E2E test: Deduplication scenario.
    - Source and destination have identical files.
    - After copy: no files should be copied/overwritten.
    """
    workspace = tmp_path / "manual_tests" / "deduplication"
    src = workspace / "src"
    dst = workspace / "dst"
    job = workspace / "job"
    src.mkdir(parents=True)
    dst.mkdir()
    # Create identical files in source and destination
    for fname in ["file1.txt", "file2.txt"]:
        (src / fname).write_text(f"This is {fname}")
        shutil.copy(src / fname, dst / fname)
    # Run workflow
    python = str(Path(".venv/Scripts/python.exe")) if Path(".venv/Scripts/python.exe").exists() else "python"
    subprocess.run([python, "fs_copy_tool/main.py", "init", "--job-dir", str(job)], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "add-source", "--job-dir", str(job), "--src", str(src)], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "destination_files"], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "copy", "--job-dir", str(job), "--dst", str(dst)], check=True)
    # Assert: files should not be changed (no overwrite)
    for fname in ["file1.txt", "file2.txt"]:
        assert (dst / fname).read_text() == f"This is {fname}"

def test_nested_directories(tmp_path):
    """
    E2E test: Nested directories scenario.
    - Source contains nested folders/files.
    - All files and structure should be copied to destination (current tool copies to dst/<full_source_path>).
    """
    workspace = tmp_path / "manual_tests" / "nested_dirs"
    src = workspace / "src"
    dst = workspace / "dst"
    job = workspace / "job"
    src.mkdir(parents=True)
    dst.mkdir()
    # Create nested structure
    (src / "a" / "b").mkdir(parents=True)
    (src / "a" / "b" / "file1.txt").write_text("nested file 1")
    (src / "a" / "file2.txt").write_text("nested file 2")
    (src / "file3.txt").write_text("root file")
    # Run workflow
    python = str(Path(".venv/Scripts/python.exe")) if Path(".venv/Scripts/python.exe").exists() else "python"
    subprocess.run([python, "fs_copy_tool/main.py", "init", "--job-dir", str(job)], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "add-source", "--job-dir", str(job), "--src", str(src)], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "source_files"], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "checksum", "--job-dir", str(job), "--table", "destination_files"], check=True)
    subprocess.run([python, "fs_copy_tool/main.py", "copy", "--job-dir", str(job), "--dst", str(dst)], check=True)
    # Assert: files are copied to dst/<full_source_path>
    assert (dst / str(src / "a" / "b" / "file1.txt")).read_text() == "nested file 1"
    assert (dst / str(src / "a" / "file2.txt")).read_text() == "nested file 2"
    assert (dst / str(src / "file3.txt")).read_text() == "root file"
