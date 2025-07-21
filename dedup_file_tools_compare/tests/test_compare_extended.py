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

def patch_uidpathutil(job_dir):
    from dedup_file_tools_commons.utils import uidpath
    orig = uidpath.UidPathUtil.reconstruct_path
    def patched(self, uid_path_obj):
        return os.path.join(job_dir, uid_path_obj.relative_path)
    uidpath.UidPathUtil.reconstruct_path = patched
    return orig

def unpatch_uidpathutil(orig):
    from dedup_file_tools_commons.utils import uidpath
    uidpath.UidPathUtil.reconstruct_path = orig

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
    orig = patch_uidpathutil(job_dir)
    try:
        ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
        ensure_pool_checksums(job_dir, job_name, 'right_pool_files')
    finally:
        unpatch_uidpathutil(orig)
    find_missing_files(db_path)
    # Check results
    from dedup_file_tools_compare.phases.results import show_result
    print('--- Identical and Different Test ---')
    show_result(db_path, summary=True)
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
    orig = patch_uidpathutil(job_dir)
    try:
        ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
        ensure_pool_checksums(job_dir, job_name, 'right_pool_files')
    finally:
        unpatch_uidpathutil(orig)
    find_missing_files(db_path)
    print('--- Missing Files Test ---')
    show_result(db_path, summary=True)
    show_result(db_path, full_report=True)

def run_all():
    tmpdir = tempfile.mkdtemp()
    try:
        test_identical_and_different(tmpdir)
        test_missing_files(tmpdir)
        print('All extended tests passed.')
    finally:
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    run_all()
