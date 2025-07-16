import os
import sqlite3
import tempfile
import shutil
from fs_copy_tool.phases.summary import summary_phase

def setup_db_with_files(statuses):
    tmpdir = tempfile.mkdtemp()
    db_path = os.path.join(tmpdir, 'copytool.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE source_files (
            uid TEXT,
            relative_path TEXT,
            size INTEGER,
            last_modified INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    cur.execute("""
        CREATE TABLE copy_status (
            uid TEXT,
            relative_path TEXT,
            status TEXT,
            last_copy_attempt INTEGER,
            error_message TEXT,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    for i, (status, error) in enumerate(statuses):
        cur.execute(
            "INSERT INTO source_files (uid, relative_path, size, last_modified) VALUES (?, ?, ?, ?)",
            (f"uid{i}", f"file{i}.dat", 100, 1234567890)
        )
        cur.execute(
            "INSERT INTO copy_status (uid, relative_path, status, last_copy_attempt, error_message) VALUES (?, ?, ?, 0, ?)",
            (f"uid{i}", f"file{i}.dat", status, error)
        )
    conn.commit()
    conn.close()
    return tmpdir, db_path

def test_summary_all_done(tmp_path):
    tmpdir, db_path = setup_db_with_files([('done', None), ('done', None)])
    summary_phase(db_path, tmpdir)
    csv_path = os.path.join(tmpdir, 'summary_report.csv')
    assert os.path.exists(csv_path)
    with open(csv_path) as f:
        lines = f.readlines()
    # Only header, no error rows
    assert len(lines) == 1
    shutil.rmtree(tmpdir)

def test_summary_with_errors_and_pending(tmp_path):
    statuses = [
        ('done', None),
        ('error', 'Disk full'),
        ('pending', None)
    ]
    tmpdir, db_path = setup_db_with_files(statuses)
    summary_phase(db_path, tmpdir)
    csv_path = os.path.join(tmpdir, 'summary_report.csv')
    assert os.path.exists(csv_path)
    with open(csv_path) as f:
        lines = f.readlines()
    # Header + 2 error/pending rows
    assert len(lines) == 3
    assert 'error' in lines[1] or 'pending' in lines[2]
    shutil.rmtree(tmpdir)
