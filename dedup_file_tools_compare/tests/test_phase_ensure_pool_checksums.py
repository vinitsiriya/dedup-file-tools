import os
from dedup_file_tools_compare.db import init_db
from dedup_file_tools_compare.phases.ensure_pool_checksums import ensure_pool_checksums
from dedup_file_tools_compare.phases.add_to_pool import add_directory_to_pool

def create_test_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_ensure_pool_checksums(tmp_path):
    job_dir = tmp_path / "job"
    left_dir = tmp_path / "left"
    job_dir.mkdir()
    left_dir.mkdir()
    create_test_file(left_dir / "a.txt", "foo")
    db_path = job_dir / "testjob_ensure.db"
    init_db(str(db_path))
    add_directory_to_pool(str(db_path), str(left_dir), 'left_pool_files')
    # Patch UidPathUtil.reconstruct_path for test
    from dedup_file_tools_commons.utils import uidpath
    orig = uidpath.UidPathUtil.reconstruct_path
    def patched(self, uid_path_obj):
        return str((job_dir.parent / uid_path_obj.relative_path).resolve())
    uidpath.UidPathUtil.reconstruct_path = patched
    try:
        ensure_pool_checksums(str(job_dir), 'testjob_ensure', 'left_pool_files')
    finally:
        uidpath.UidPathUtil.reconstruct_path = orig
    print('ensure_pool_checksums phase test passed.')
