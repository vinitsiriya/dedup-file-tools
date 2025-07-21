import pytest
from dedup_file_tools_compare import main

def create_test_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def test_cli_workflow(tmp_path):
    job_dir = tmp_path / "job"
    left_dir = tmp_path / "left"
    right_dir = tmp_path / "right"
    job_dir.mkdir()
    left_dir.mkdir()
    right_dir.mkdir()
    create_test_file(left_dir / "a.txt", "foo")
    create_test_file(right_dir / "b.txt", "bar")
    job_name = "testjob_cli"
    # Patch UidPathUtil.reconstruct_path for test
    from dedup_file_tools_commons.utils import uidpath
    orig_reconstruct_path = uidpath.UidPathUtil.reconstruct_path
    def test_reconstruct_path(self, uid_path_obj):
        return str((job_dir.parent / uid_path_obj.relative_path).resolve())
    uidpath.UidPathUtil.reconstruct_path = test_reconstruct_path
    try:
        # Add to left pool
        args = main.parse_args(["add-to-left", "--job-dir", str(job_dir), "--job-name", job_name, "--dir", str(left_dir)])
        assert main.run_main_command(args) == 0
        # Add to right pool
        args = main.parse_args(["add-to-right", "--job-dir", str(job_dir), "--job-name", job_name, "--dir", str(right_dir)])
        assert main.run_main_command(args) == 0
        # Find missing files
        args = main.parse_args(["find-missing-files", "--job-dir", str(job_dir), "--job-name", job_name])
        assert main.run_main_command(args) == 0
        # Show result
        args = main.parse_args(["show-result", "--job-dir", str(job_dir), "--job-name", job_name, "--summary"])
        assert main.run_main_command(args) == 0
        print('CLI workflow test passed.')
    finally:
        uidpath.UidPathUtil.reconstruct_path = orig_reconstruct_path