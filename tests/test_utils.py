import os
import sqlite3
import tempfile
from fs_copy_tool.utils.uidpath import UidPath
from fs_copy_tool.utils.fileops import compute_sha256, copy_file, verify_file
from fs_copy_tool.phases.analysis import analyze_volumes
from fs_copy_tool.phases.checksum import update_checksums
from fs_copy_tool.phases.copy import copy_files

def test_compute_sha256(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello world")
    assert compute_sha256(file) == compute_sha256(file)

def test_copy_and_verify(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data123")
    copy_file(src, dst)
    assert verify_file(src, dst)

def test_uidpath(tmp_path):
    uidpath = UidPath()
    # Should not raise
    uidpath.update_mounts()
    assert isinstance(uidpath.get_available_volumes(), dict)
