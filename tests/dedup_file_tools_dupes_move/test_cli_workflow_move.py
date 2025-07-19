import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_dupes_move.main import main

def test_cli_workflow_move(tmp_path):
    dupes_folder = tmp_path / "dupes"
    removal_folder = tmp_path / "removal"
    job_dir = tmp_path / "job"
    # Create subdirectories and files
    (dupes_folder / "a").mkdir(parents=True)
    (dupes_folder / "b").mkdir(parents=True)
    removal_folder.mkdir()
    job_dir.mkdir()
    # True duplicate: a/file0.txt and b/file0.txt
    (dupes_folder / "a" / "file0.txt").write_text("hello")
    (dupes_folder / "b" / "file0.txt").write_text("hello")
    # Unique files
    for i in range(1, 5):
        (dupes_folder / "a" / f"file{i}.txt").write_text(f"unique{i}")
    job_name = "testjob"

    steps = [
        ["init", "--job-dir", str(job_dir), "--job-name", job_name],
        ["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(dupes_folder)],
        ["preview-summary", "--job-dir", str(job_dir), "--job-name", job_name],
        ["move", "--job-dir", str(job_dir), "--job-name", job_name, "--dupes-folder", str(removal_folder)],
        ["verify", "--job-dir", str(job_dir), "--job-name", job_name],
        ["summary", "--job-dir", str(job_dir), "--job-name", job_name],
    ]
    for args in steps:
        try:
            main(args)
        except SystemExit as e:
            if e.code != 0:
                raise
    # Check for moved duplicate (should preserve relative path)
    moved_files = list(removal_folder.rglob("file0.txt"))
    assert len(moved_files) == 1
    # The moved file should be from either a/file0.txt or b/file0.txt
    assert moved_files[0].name == "file0.txt"

    # Stricter: Only one file0.txt remains in the source (dupes_folder)
    remaining_file0 = list(dupes_folder.rglob("file0.txt"))
    assert len(remaining_file0) == 1, f"Expected only one file0.txt in source, found: {remaining_file0}"
    # The moved file is not present in the source
    assert moved_files[0].resolve() != remaining_file0[0].resolve(), "Moved file should not remain in source"

    # All unique files remain untouched
    for i in range(1, 5):
        unique_file = dupes_folder / "a" / f"file{i}.txt"
        assert unique_file.exists(), f"Unique file {unique_file} missing after move"

    # The summary CSV exists
    summary_csv = job_dir / "dedup_move_summary.csv"
    assert summary_csv.exists()
