import pytest
import os
from dedup_file_tools_dupes_move.main import main

def test_one_shot_command(tmp_path):
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    removal = tmp_path / "removal"
    src.mkdir()
    removal.mkdir()
    job_dir.mkdir()
    # Create duplicate and unique files
    (src / "a.txt").write_text("dupe")
    (src / "b.txt").write_text("dupe")
    (src / "c.txt").write_text("unique")
    job_name = "one_shot"
    # Run the one-shot workflow
    main([
        "one-shot",
        "--job-dir", str(job_dir),
        "--job-name", job_name,
        "--lookup-pool", str(src),
        "--dupes-folder", str(removal)
    ])
    # Check that one of the duplicate files was moved
    moved_files = list(removal.glob("*.txt"))
    assert any(f.name == "a.txt" or f.name == "b.txt" for f in moved_files)
    # Check that the unique file was not moved
    assert not (removal / "c.txt").exists()
    # Check that summary CSV exists
    csv_path = job_dir / "dedup_move_summary.csv"
    assert csv_path.exists()
    # Check that the database has correct status counts
    import sqlite3
    db_path = str(job_dir / f"{job_name}.db")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT status, COUNT(*) FROM dedup_move_plan GROUP BY status")
        status_counts = dict(cur.fetchall())
        assert status_counts.get("verified", 0) == 2
        # After verification, all keepers should be marked as verified
