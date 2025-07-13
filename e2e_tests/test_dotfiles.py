"""
Test: Dotfiles/hidden files
"""
import subprocess
import tempfile
from pathlib import Path
import os
import sys

def run_quiet(cmd, env=None):
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)

def get_python_exec():
    venv_exec = Path(os.getcwd()) / '.venv' / 'Scripts' / 'python.exe'
    if venv_exec.exists():
        return str(venv_exec)
    return sys.executable

def test_dotfile():
    python_exec = get_python_exec()
    env = os.environ.copy()
    env['VIRTUAL_ENV'] = str(Path(os.getcwd()) / '.venv')
    env['PATH'] = str(Path(os.getcwd()) / '.venv' / 'Scripts') + os.pathsep + env.get('PATH', '')
    src = Path(tempfile.mkdtemp())
    dst = Path(tempfile.mkdtemp())
    (src / '.hidden_file').write_text('hidden', encoding='utf-8')
    job_dir = Path(tempfile.mkdtemp())
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'init', '--job-dir', str(job_dir)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'analyze', '--job-dir', str(job_dir), '--src', str(src)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'analyze', '--job-dir', str(job_dir), '--dst', str(dst)], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'checksum', '--job-dir', str(job_dir), '--table', 'source_files'], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'checksum', '--job-dir', str(job_dir), '--table', 'destination_files'], env)
    run_quiet([python_exec, '-m', 'fs_copy_tool.main', 'copy', '--job-dir', str(job_dir), '--src', str(src), '--dst', str(dst)], env)
    assert (dst / '.hidden_file').exists(), ".hidden_file not copied"
    assert (dst / '.hidden_file').read_text(encoding='utf-8') == 'hidden'
