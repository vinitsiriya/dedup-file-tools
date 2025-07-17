import os
import sqlite3
import logging
from pathlib import Path
from dedup_file_tools_fs_copy.utils.uidpath import UidPathUtil
from .destination_pool import DestinationPoolIndex

def add_to_destination_index_pool(db_path, dst_root):
    """
    Recursively scan dst_root and add/update all files in the destination pool index.
    """
    uid_path = UidPathUtil()
    pool = DestinationPoolIndex(db_path, uid_path)
    dst_root = Path(dst_root)
    from tqdm import tqdm
    count = 0
    # dst_root.rglob("*") is already an iterator, so this is scalable
    with tqdm(desc=f"Indexing destination pool from {dst_root}", unit="file") as pbar:
        for path in dst_root.rglob("*"):
            if path.is_file():
                stat = path.stat()
                pool.add_or_update_file(str(path), stat.st_size, int(stat.st_mtime))
                logging.info(f"Added/updated file in destination pool index: {path}")
                count += 1
                pbar.update(1)
                if count % 10000 == 0:
                    logging.info(f"Discovered {count} files so far in {dst_root}")
    logging.info(f"Batch add/update complete: {count} files processed in destination pool index from {dst_root}")
