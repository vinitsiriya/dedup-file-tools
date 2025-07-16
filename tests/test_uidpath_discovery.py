def test_pytest_discovery():
    assert True
    print('Pytest discovery works!')

import os
import sqlite3
import tempfile
import pytest
from pathlib import Path
from fs_copy_tool.utils.uidpath import UidPathUtil, UidPath

def test_convert_and_reconstruct(tmp_path):
    uid_path = UidPathUtil()
    file_path = tmp_path / "afile.txt"
    file_path.write_text("abc")
    uid_path_obj = uid_path.convert_path(str(file_path))
    assert uid_path_obj.uid is not None
    abs_path = uid_path.reconstruct_path(uid_path_obj)
    assert abs_path is not None
    assert abs_path.resolve() == file_path.resolve()

def test_is_conversion_reversible(tmp_path):
    uid_path = UidPathUtil()
    file_path = tmp_path / "bfile.txt"
    file_path.write_text("def")
    uid_path_obj = uid_path.convert_path(str(file_path))
    assert uid_path.is_conversion_reversible(str(file_path))

def test_get_mounts_and_uids():
    uid_path = UidPathUtil()
    mounts = uid_path.get_available_volumes()
    uids = uid_path.get_available_uids()
    assert isinstance(mounts, dict)
    assert isinstance(uids, set)
    assert len(mounts) > 0
    assert len(uids) > 0

def test_nested_directory_conversion(tmp_path):
    uid_path = UidPathUtil()
    nested_dir = tmp_path / "subdir1" / "subdir2"
    nested_dir.mkdir(parents=True)
    file_path = nested_dir / "nested.txt"
    file_path.write_text("nested content")
    uid_path_obj = uid_path.convert_path(str(file_path))
    assert uid_path_obj.uid is not None
    abs_path = uid_path.reconstruct_path(uid_path_obj)
    assert abs_path.resolve() == file_path.resolve()

def test_get_mount_point_and_label():
    uid_path = UidPathUtil()
    mounts = uid_path.get_available_volumes()
    for mount, uid in mounts.items():
        if uid is None:
            continue  # skip invalid
        # get_mount_point_from_volume_id should return the mount
        assert uid_path.get_mount_point_from_volume_id(uid) == mount or os.path.isdir(uid)
        # get_volume_label_from_drive_letter should not error (Windows only)
        if uid_path.os == "Windows":
            label = uid_path.get_volume_label_from_drive_letter(mount)
            assert isinstance(label, str)

def test_invalid_path_conversion():
    uid_path = UidPathUtil()
    # Path that does not exist should still return a rel_path
    uid_path_obj = uid_path.convert_path("/this/path/does/not/exist.txt")
    # UID may be None if not under a known mount
    assert isinstance(uid_path_obj.relative_path, str)

def test_is_volume_available():
    uid_path = UidPathUtil()
    uids = uid_path.get_available_uids()
    for uid in uids:
        if uid is None:
            continue  # skip invalid
        # skip pseudo-volume UIDs that are directory paths (test env)
        if isinstance(uid, str) and (os.path.sep in uid or os.path.isdir(uid)):
            continue
        assert uid_path.is_volume_available(uid)
