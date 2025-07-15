import os
import sqlite3
from pathlib import Path
from fs_copy_tool.utils.uidpath import UidPath
from .destination_pool import DestinationPoolIndex

def add_to_destination_index_pool(db_path, dst_root):
    """
    Recursively scan dst_root and add/update all files in the destination pool index.
    """
    uid_path = UidPath()
    pool = DestinationPoolIndex(db_path, uid_path)
    dst_root = Path(dst_root)
    count = 0
    for file in dst_root.rglob("*"):
        if file.is_file():
            stat = file.stat()
            pool.add_or_update_file(str(file), stat.st_size, int(stat.st_mtime))
            count += 1
    print(f"Added/updated {count} files in destination pool index from {dst_root}")
