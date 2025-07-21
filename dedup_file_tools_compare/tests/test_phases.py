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

def test_add_to_pool(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob_add'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    create_test_file(os.path.join(job_dir, 'left', 'a.txt'), 'foo')
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    conn = None
    try:
        conn = __import__('sqlite3').connect(db_path)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM left_pool_files')
        count = cur.fetchone()[0]
        assert count == 1
        print('add_to_pool phase test passed.')
    finally:
        if conn:
            conn.close()

def test_ensure_pool_checksums(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob_ensure'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    create_test_file(os.path.join(job_dir, 'left', 'a.txt'), 'foo')
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    orig = patch_uidpathutil(job_dir)
    try:
        ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
        print('ensure_pool_checksums phase test passed.')
    finally:
        unpatch_uidpathutil(orig)

def test_find_missing_files(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob_find'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    os.makedirs(os.path.join(job_dir, 'right'), exist_ok=True)
    create_test_file(os.path.join(job_dir, 'left', 'a.txt'), 'foo')
    create_test_file(os.path.join(job_dir, 'right', 'b.txt'), 'bar')
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
    print('find_missing_files phase test passed.')

def test_show_result(tmpdir):
    job_dir = tmpdir
    job_name = 'testjob_show'
    db_path = os.path.join(job_dir, f'{job_name}.db')
    os.makedirs(os.path.join(job_dir, 'left'), exist_ok=True)
    create_test_file(os.path.join(job_dir, 'left', 'a.txt'), 'foo')
    init_db(db_path)
    add_directory_to_pool(db_path, os.path.join(job_dir, 'left'), 'left_pool_files')
    orig = patch_uidpathutil(job_dir)
    try:
        ensure_pool_checksums(job_dir, job_name, 'left_pool_files')
    finally:
        unpatch_uidpathutil(orig)
    find_missing_files(db_path)
    show_result(db_path, summary=True)
    print('show_result phase test passed.')

def run_all():
    tmpdir = tempfile.mkdtemp()
    try:
        test_add_to_pool(tmpdir)
        test_ensure_pool_checksums(tmpdir)
        test_find_missing_files(tmpdir)
        test_show_result(tmpdir)
        print('All phase tests passed.')
    finally:
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    run_all()
