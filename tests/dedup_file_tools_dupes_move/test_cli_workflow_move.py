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
    dupes_folder.mkdir()
    removal_folder.mkdir()
    job_dir.mkdir()
    (dupes_folder / "a.txt").write_text("hello")
    (dupes_folder / "b.txt").write_text("hello")
    (dupes_folder / "c.txt").write_text("unique")
    job_name = "testjob"

    steps = [
        ["init", "--job-dir", str(job_dir), "--job-name", job_name],
        ["add-to-lookup-pool", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(dupes_folder)],
        ["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(dupes_folder)],
        ["preview-summary", "--job-dir", str(job_dir), "--job-name", job_name],
        ["move", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(dupes_folder), "--dupes-folder", str(removal_folder)],
        ["verify", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(dupes_folder), "--dupes-folder", str(removal_folder)],
        ["summary", "--job-dir", str(job_dir), "--job-name", job_name],
    ]
    for args in steps:
        try:
            main(args)
        except SystemExit as e:
            if e.code != 0:
                raise
    moved_files = list(removal_folder.glob("*.txt"))
    assert any(f.name == "a.txt" or f.name == "b.txt" for f in moved_files)
    summary_csv = job_dir / "dedup_move_summary.csv"
    assert summary_csv.exists()
