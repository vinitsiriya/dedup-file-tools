"""
E2E Test Cases: fs-copy-tool

Each test uses its own fixture directory and verifies a specific scenario step by step.
"""
import subprocess
import tempfile
import shutil
from pathlib import Path
import os
import sys
import pytest

def run_quiet(cmd, env=None):
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

def get_python_exec():
    venv_exec = Path(os.getcwd()) / '.venv' / 'Scripts' / 'python.exe'
    if venv_exec.exists():
        return str(venv_exec)
    return sys.executable

def setup_job_dir():
    return Path(tempfile.mkdtemp())

def setup_fixture_dir(name):
    base = Path(tempfile.mkdtemp()) / name
    src = base / 'src'
    dst = base / 'dst'
    src.mkdir(parents=True)
    dst.mkdir(parents=True)
    return base, src, dst

@pytest.mark.parametrize("filename,content", [
    ("file1.txt", "hello world"),
    (".dotfile", "hidden"),
    ("unicodé_文件.txt", "unicode content"),
])
def test_single_file(filename, content):
    python_exec = get_python_exec()
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(Path(os.getcwd()) / '.venv')
    env['PATH'] = str(Path(os.getcwd()) / '.venv' / 'Scripts') + os.pathsep + env.get('PATH', '')
    base, src, dst = setup_fixture_dir('single_file')
    (src / filename).write_text(content, encoding='utf-8')
    job_dir = setup_job_dir()
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'init', '--job-dir', str(job_dir)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'add-file', '--job-dir', str(job_dir), '--file', str(src / filename)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'analyze', '--job-dir', str(job_dir), '--dst', str(dst)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'checksum', '--job-dir', str(job_dir), '--table', 'source_files'], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'checksum', '--job-dir', str(job_dir), '--table', 'destination_files'], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'copy', '--job-dir', str(job_dir), '--src', str(src), '--dst', str(dst)], env)
    # Assert file copied
    assert (dst / filename).exists(), f"{filename} not copied"
    assert (dst / filename).read_text(encoding='utf-8') == content

def test_duplicate_files():
    python_exec = get_python_exec()
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(Path(os.getcwd()) / '.venv')
    env['PATH'] = str(Path(os.getcwd()) / '.venv' / 'Scripts') + os.pathsep + env.get('PATH', '')
    base, src, dst = setup_fixture_dir('dup_files')
    (src / "a.txt").write_text("abc")
    (src / "b.txt").write_text("abc")
    job_dir = setup_job_dir()
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'init', '--job-dir', str(job_dir)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'add-source', '--job-dir', str(job_dir), '--src', str(src)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'analyze', '--job-dir', str(job_dir), '--dst', str(dst)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'checksum', '--job-dir', str(job_dir), '--table', 'source_files'], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'checksum', '--job-dir', str(job_dir), '--table', 'destination_files'], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'copy', '--job-dir', str(job_dir), '--src', str(src), '--dst', str(dst)], env)
    # Assert only one file is copied due to deduplication
    copied = [f for f in [dst / "a.txt", dst / "b.txt"] if f.exists()]
    assert len(copied) == 1, f"Expected only one file to be copied, but found: {[str(f) for f in copied]}"
    assert copied[0].read_text(encoding='utf-8') == "abc"
