"""
File: fs-copy-tool/phases/analysis.py
Description: Analysis phase logic (scanning and metadata extraction)
"""
import logging
import sqlite3
from fs_copy_tool.utils.uidpath import UidPath
from fs_copy_tool.utils.fileops import compute_sha256
from pathlib import Path
import os

def persist_file_metadata(db_path, table, file_info):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {table} (uid, relative_path, size, last_modified, checksum_stale)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(uid, relative_path) DO UPDATE SET
                size=excluded.size,
                last_modified=excluded.last_modified,
                checksum_stale=1
        """, (file_info['uid'], file_info['relative_path'], file_info['size'], file_info['last_modified']))
        conn.commit()

def scan_files_on_volume(volume_root, uid_path: UidPath):
    # If the volume_root is a directory, treat it as its own mount (for tests and general robustness)
    if os.path.isdir(volume_root):
        mount_id = volume_root
        mountpoint = volume_root
    else:
        mount_id = uid_path.get_volume_id_from_path(volume_root)
        mountpoint = uid_path.get_mount_point_from_volume_id(mount_id)
    if not mountpoint:
        logging.error(f"Mount point not found for volume {mount_id}")
        return
    for file in Path(mountpoint).rglob("*"):
        if file.is_file():
            rel = str(file.relative_to(mountpoint))
            stat = file.stat()
            yield {
                'uid': mount_id,
                'relative_path': rel,
                'size': stat.st_size,
                'last_modified': int(stat.st_mtime)
            }

def analyze_volumes(db_path, volume_roots, table):
    uid_path = UidPath()
    for root in volume_roots:
        for file_info in scan_files_on_volume(root, uid_path):
            persist_file_metadata(db_path, table, file_info)
            logging.info(f"Indexed: {file_info['uid']}:{file_info['relative_path']}")
