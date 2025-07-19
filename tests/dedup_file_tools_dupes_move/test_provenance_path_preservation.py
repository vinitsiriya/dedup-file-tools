import os
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_dupes_move.main import main

def test_pool_base_path_and_path_preservation(tmp_path):
    pool1 = tmp_path / "pool1"
    pool2 = tmp_path / "pool2"
    removal = tmp_path / "removal"
    job_dir = tmp_path / "job"
    pool1.mkdir()
    pool2.mkdir()
    removal.mkdir()
    job_dir.mkdir()
    # Create duplicate files with same name in different pools
    (pool1 / "subdir" ).mkdir()
    (pool2 / "subdir" ).mkdir()
    (pool1 / "subdir" / "dupe.txt").write_text("dupe-content")
    (pool2 / "subdir" / "dupe.txt").write_text("dupe-content")
    # Unique files
    (pool1 / "unique1.txt").write_text("unique1")
    (pool2 / "unique2.txt").write_text("unique2")
    job_name = "provenance"
    # Analyze both pools
    main(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(pool1)])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(pool2)])
    main(["move", "--job-dir", str(job_dir), "--job-name", job_name, "--dupes-folder", str(removal)])
    # Check dedup_files_pool for correct pool_base_path
    db_path = str(job_dir / f"{job_name}.db")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT relative_path, pool_base_path FROM dedup_files_pool")
        rows = cur.fetchall()
        for rel_path, pool_base_path in rows:
            assert pool_base_path in (str(pool1.resolve()), str(pool2.resolve())), f"Unexpected pool_base_path: {pool_base_path}"
    # Check that moved file is in correct relative path in removal dir
    moved_files = list(removal.rglob("dupe.txt"))
    assert len(moved_files) == 1
    rel = moved_files[0].relative_to(removal)
    # Should be subdir/dupe.txt
    assert rel.parts[0] == "subdir"
    # Only one dupe.txt remains in pools
    remaining = list(pool1.rglob("dupe.txt")) + list(pool2.rglob("dupe.txt"))
    assert len(remaining) == 1
    # Unique files remain
    assert (pool1 / "unique1.txt").exists()
    assert (pool2 / "unique2.txt").exists()
