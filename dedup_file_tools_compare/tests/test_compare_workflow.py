import os
import sqlite3
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

def test_compare_basic(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'right'), exist_ok=True)
    # Create files
    create_test_file(os.path.join(job_dir, 'left', 'a.txt'), 'foo')
    create_test_file(os.path.join(job_dir, 'left', 'b.txt'), 'bar')
    create_test_file(os.path.join(job_dir, 'right', 'a.txt'), 'foo')
    create_test_file(os.path.join(job_dir, 'right', 'c.txt'), 'baz')
    # Init DB and add to pools
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    add_directory_to_pool(db_path, os.path.join(job_dir, 'right'), 'right_pool_files')
    # Patch UidPathUtil.reconstruct_path for test
    from dedup_file_tools_commons.utils import uidpath
    orig_reconstruct_path = uidpath.UidPathUtil.reconstruct_path
    def test_reconstruct_path(self, uid_path_obj):
        # Just join the tempdir, uid, and rel_path for test
        return os.path.join(job_dir, uid_path_obj.relative_path)
    uidpath.UidPathUtil.reconstruct_path = test_reconstruct_path
    try:
        # Ensure checksums
        ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
        ensure_pool_checksums(job_dir, job_name, 'right_pool_files')
    finally:
        uidpath.UidPathUtil.reconstruct_path = orig_reconstruct_path
    # Compare
    find_missing_files(db_path)
    # Show result (should print summary)
    show_result(db_path, summary=True)

def run_all():
    tmpdir = tempfile.mkdtemp()
    try:
        test_compare_basic(tmpdir)
        print('All tests passed.')
    finally:
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    run_all()
