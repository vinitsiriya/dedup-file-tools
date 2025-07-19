import os
import shutil
import tempfile
import pytest
from dedup_file_tools_dupes_move.main import main


def test_analysis_detects_no_duplicates(tmp_path):
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    src.mkdir()
    job_dir.mkdir()
    (src / "a.txt").write_text("one")
    (src / "b.txt").write_text("two")
    (src / "c.txt").write_text("three")
    job_name = "no_dupes"
    main(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src)])
    # Preview summary should show 0 planned moves
    from dedup_file_tools_dupes_move.phases.preview_summary import preview_summary
    db_path = str(job_dir / f"{job_name}.db")
    preview_summary(db_path)
    # Check DB directly
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM dedup_move_plan WHERE status='planned'")
        planned = cur.fetchone()[0]
        assert planned == 0


def test_move_handles_missing_file(tmp_path):
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    removal = tmp_path / "removal"
    src.mkdir()
    removal.mkdir()
    job_dir.mkdir()
    (src / "a.txt").write_text("dupe")
    (src / "b.txt").write_text("dupe")
    job_name = "missing_file"
    main(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src)])
    # Remove one file before move
    os.remove(src / "b.txt")
    main(["move", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src), "--dupes-folder", str(removal)])
    # Should log error but not crash; check DB for error status
    import sqlite3
    db_path = str(job_dir / f"{job_name}.db")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM dedup_move_plan WHERE status='error'")
        errors = cur.fetchone()[0]
        assert errors > 0


def test_verify_detects_checksum_mismatch(tmp_path):
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    removal = tmp_path / "removal"
    src.mkdir()
    removal.mkdir()
    job_dir.mkdir()
    (src / "a.txt").write_text("dupe")
    (src / "b.txt").write_text("dupe")
    job_name = "verify_mismatch"
    main(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src)])
    main(["move", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src), "--dupes-folder", str(removal)])
    # Corrupt the original keeper file (since verify checks original location)
    for f in src.iterdir():
        f.write_text("corrupted")
    main(["verify", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src), "--dupes-folder", str(removal)])
    # Check DB for error status
    import sqlite3
    db_path = str(job_dir / f"{job_name}.db")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM dedup_move_plan WHERE status='error'")
        errors = cur.fetchone()[0]
        assert errors > 0


def test_summary_csv_output(tmp_path):
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    removal = tmp_path / "removal"
    src.mkdir()
    removal.mkdir()
    job_dir.mkdir()
    (src / "a.txt").write_text("dupe")
    (src / "b.txt").write_text("dupe")
    job_name = "summary_csv"
    main(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src)])
    main(["move", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src), "--dupes-folder", str(removal)])
    main(["summary", "--job-dir", str(job_dir), "--job-name", job_name])
    csv_path = job_dir / "dedup_move_summary.csv"
    assert csv_path.exists()
    with open(csv_path, "r", encoding="utf-8") as f:
        header = f.readline()
        assert "uid" in header and "relative_path" in header
        lines = f.readlines()
        assert len(lines) > 0


def test_preview_summary_output(tmp_path, capsys):
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    src.mkdir()
    job_dir.mkdir()
    (src / "a.txt").write_text("dupe")
    (src / "b.txt").write_text("dupe")
    job_name = "preview"
    main(["init", "--job-dir", str(job_dir), "--job-name", job_name])
    main(["analyze", "--job-dir", str(job_dir), "--job-name", job_name, "--lookup-pool", str(src)])
    main(["preview-summary", "--job-dir", str(job_dir), "--job-name", job_name])
    out = capsys.readouterr().out
    assert "Planned duplicate groups" in out
    assert "Files to be moved" in out
    assert "Move:" in out
