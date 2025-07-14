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
from tqdm import tqdm

def persist_file_metadata(db_path, table, file_info):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {table} (uid, relative_path, size, last_modified)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(uid, relative_path) DO UPDATE SET
                size=excluded.size,
                last_modified=excluded.last_modified
        """, (file_info['uid'], file_info['relative_path'], file_info['size'], file_info['last_modified']))
        conn.commit()

def scan_files_on_volume(volume_root, uid_path: UidPath):
    # Always use UidPath.convert_path for every file, even in test directories
    mountpoint = volume_root if os.path.isdir(volume_root) else uid_path.get_mount_point_from_volume_id(uid_path.get_volume_id_from_path(volume_root))
    if not mountpoint:
        logging.error(f"Mount point not found for volume {volume_root}")
        return
    for file in Path(mountpoint).rglob("*"):
        if file.is_file():
            uid, rel = uid_path.convert_path(str(file))
            if uid is None:
                logging.error(f"Could not determine UID for file {file}")
                continue
            stat = file.stat()
            logging.info(f"[AGENT][ANALYZE] Indexed: {file}")
            yield {
                'uid': uid,
                'relative_path': rel,
                'size': stat.st_size,
                'last_modified': int(stat.st_mtime)
            }

def analyze_volumes(db_path, volume_roots, table):
    uid_path = UidPath()
    total_files = 0
    # First, count total files for progress bar
    for root in volume_roots:
        for _ in scan_files_on_volume(root, uid_path):
            total_files += 1
    if total_files == 0:
        return
    # Now process with progress bar
    with tqdm(total=total_files, desc=f"Analyzing {table}") as pbar:
        for root in volume_roots:
            for file_info in scan_files_on_volume(root, uid_path):
                persist_file_metadata(db_path, table, file_info)
                logging.info(f"Indexed: {file_info['uid']}:{file_info['relative_path']}")
                pbar.update(1)
