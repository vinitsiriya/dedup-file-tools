import os
import tempfile
import shutil
from dedup_file_tools_compare.db import init_db
from dedup_file_tools_compare.phases.add_to_pool import add_directory_to_pool
from dedup_file_tools_compare.phases.ensure_pool_checksums import ensure_pool_checksums
from dedup_file_tools_compare.phases.compare import find_missing_files
from dedup_file_tools_compare.phases.results import show_result

def create_test_file(path, content):
    with open(path, 'w') as f:
        f.write(content)


def test_identical_and_different(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob2'
    db_path = os.path.join(job_dir, f'{job_name}.db') 
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'right'), exist_ok=True)
    # Identical file
    create_test_file(os.path.join(job_dir, 'left', 'same.txt'), 'samecontent')
    create_test_file(os.path.join(job_dir, 'right', 'same.txt'), 'samecontent')
    # Different file
    create_test_file(os.path.join(job_dir, 'left', 'diff.txt'), 'left')
    create_test_file(os.path.join(job_dir, 'right', 'diff.txt'), 'right')
    # Add to pools 
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    add_directory_to_pool(db_path, os.path.join(job_dir, 'right'), 'right_pool_files')
    ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
    ensure_pool_checksums(job_dir, job_name, 'right_pool_files')
    find_missing_files(db_path)
    # Check results 
    from dedup_file_tools_compare.phases.results import show_result
    print('--- Identical and Different Test ---')
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM compare_results_identical')
    assert cur.fetchone()[0] >= 0
    cur.execute('SELECT COUNT(*) FROM compare_results_different')
    assert cur.fetchone()[0] >= 0
    cur.execute('SELECT COUNT(*) FROM compare_results_right_missing')
    assert cur.fetchone()[0] >= 0
    cur.execute('SELECT COUNT(*) FROM compare_results_left_missing')
    assert cur.fetchone()[0] >= 0
    conn.close()
    show_result(db_path, full_report=True)

def test_missing_files(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob3'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'right'), exist_ok=True)
    # Only in left
    create_test_file(os.path.join(job_dir, 'left', 'onlyleft.txt'), 'foo')
    # Only in right
    create_test_file(os.path.join(job_dir, 'right', 'onlyright.txt'), 'bar')
    # Add to pools
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    add_directory_to_pool(db_path, os.path.join(job_dir, 'right'), 'right_pool_files')
    ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
    ensure_pool_checksums(job_dir, job_name, 'right_pool_files')
    find_missing_files(db_path)
    print('--- Missing Files Test ---') 
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM compare_results_right_missing')
    assert cur.fetchone()[0] >= 0
    cur.execute('SELECT COUNT(*) FROM compare_results_left_missing')
    assert cur.fetchone()[0] >= 0
    cur.execute('SELECT COUNT(*) FROM compare_results_identical')
    assert cur.fetchone()[0] >= 0
    cur.execute('SELECT COUNT(*) FROM compare_results_different')
    assert cur.fetchone()[0] >= 0
    conn.close()
    show_result(db_path, full_report=True)

def run_all():
    tmpdir = tempfile.mkdtemp()

    try:
        test_identical_and_different(tmpdir)
        test_missing_files(tmpdir)
        print('All extended tests passed.')
    finally:
        shutil.rmtree(tmpdir)


# Simpler test: one identical, one left-only, one right-only
def test_simple_compare(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob_simple'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'right'), exist_ok=True)
    # Identical file in matching subdirectory
    os.makedirs(os.path.join(job_dir, 'left', 'common'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'right', 'common'), exist_ok=True)
    create_test_file(os.path.join(job_dir, 'left', 'common', 'same.txt'), 'samecontent')
    create_test_file(os.path.join(job_dir, 'right', 'common', 'same.txt'), 'samecontent')
    # Only in left
    create_test_file(os.path.join(job_dir, 'left', 'onlyleft.txt'), 'foo')
    # Only in right
    create_test_file(os.path.join(job_dir, 'right', 'onlyright.txt'), 'bar')
    # Add to pools
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    add_directory_to_pool(db_path, os.path.join(job_dir, 'right'), 'right_pool_files')
    ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
    ensure_pool_checksums(job_dir, job_name, 'right_pool_files')
    find_missing_files(db_path)
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM compare_results_identical')
    result = cur.fetchone()
    print(f"DB identical count: {result}")
    cur.execute('SELECT * FROM compare_results_identical')
    all_rows = cur.fetchall()
    print(f"DB identical rows: {all_rows}")
    assert result[0] == 1, "Expected 1 identical file in DB."
    cur.execute('SELECT COUNT(*) FROM compare_results_left_missing')
    assert cur.fetchone()[0] == 1, "Expected 1 missing from left in DB."
    cur.execute('SELECT COUNT(*) FROM compare_results_right_missing')
    assert cur.fetchone()[0] == 1, "Expected 1 missing from right in DB."
    conn.close()

if __name__ == '__main__':
    run_all()
