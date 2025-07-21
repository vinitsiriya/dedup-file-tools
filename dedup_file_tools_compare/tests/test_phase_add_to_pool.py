import os
import tempfile
import shutil
from dedup_file_tools_compare.db import init_db
from dedup_file_tools_compare.phases.add_to_pool import add_directory_to_pool

def create_test_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_add_to_pool(tmp_path):
    job_dir = tmp_path / "job"
    left_dir = tmp_path / "left"
    job_dir.mkdir()
    left_dir.mkdir()
    create_test_file(left_dir / "a.txt", "foo")
    db_path = job_dir / "testjob_add.db"
    init_db(str(db_path))
    add_directory_to_pool(str(db_path), str(left_dir), 'left_pool_files')
    import sqlite3
    with sqlite3.connect(str(db_path)) as conn:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM left_pool_files')
        count = cur.fetchone()[0]
        assert count == 1
    print('add_to_pool phase test passed.')
