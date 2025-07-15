import os
import sqlite3
import tempfile
import shutil
from pathlib import Path
from fs_copy_tool.utils.destination_pool_cli import add_to_destination_index_pool
from fs_copy_tool.utils.destination_pool import DestinationPoolIndex
from fs_copy_tool.utils.uidpath import UidPath

def test_add_to_destination_index_pool(tmp_path):
    db_path = tmp_path / "test.db"
    # Create the destination_pool_files table
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE destination_pool_files (
            uid TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            size INTEGER,
            last_modified INTEGER,
            last_seen INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    conn.commit()
    conn.close()
    # Create a destination root with files
    dst_root = tmp_path / "dst"
    dst_root.mkdir()
    file1 = dst_root / "file1.txt"
    file2 = dst_root / "file2.txt"
    file1.write_text("foo")
    file2.write_text("bar")
    # Run the CLI logic
    add_to_destination_index_pool(str(db_path), str(dst_root))
    # Check that both files are in the pool index
    uid_path = UidPath()
    pool = DestinationPoolIndex(str(db_path), uid_path)
    uid1, rel1 = uid_path.convert_path(str(file1))
    uid2, rel2 = uid_path.convert_path(str(file2))
    assert pool.exists(uid1, str(rel1))
    assert pool.exists(uid2, str(rel2))
