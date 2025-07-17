"""
File: dedup_file_tools_fs_copy/phases/analysis.py

Analysis Phase Module
---------------------
This module implements the analysis phase for the deduplication/copy tool. It is responsible for:
- Scanning a given volume or directory recursively for all files.
- Extracting and persisting file metadata (UID, relative path, size, last modified time) to the database.
- Using UidPath abstraction for robust, cross-platform file identification.
- Providing progress feedback via tqdm.

All file metadata is stored in the specified table (e.g., source_files or destination_files) for later processing in copy, verify, and summary phases.
"""
import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from pathlib import Path
import os
from tqdm import tqdm

def persist_file_metadata(db_path, table, file_info):
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute(f"""
            INSERT INTO {table} (uid, relative_path, size, last_modified)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(uid, relative_path) DO UPDATE SET
                size=excluded.size,
                last_modified=excluded.last_modified
        """, (file_info['uid'], file_info['relative_path'], file_info['size'], file_info['last_modified']))
        conn.commit()

def scan_files_on_volume(volume_root, uid_path: UidPathUtil):
    # Always use UidPath.convert_path for every file, even in test directories
    mountpoint = volume_root if os.path.isdir(volume_root) else uid_path.get_mount_point_from_volume_id(uid_path.get_volume_id_from_path(volume_root))
    if not mountpoint:
        logging.error(f"Mount point not found for volume {volume_root}")
        return
    for file in Path(mountpoint).rglob("*"):
        if file.is_file():
            uid_path_obj = uid_path.convert_path(str(file))
            uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
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
    import concurrent.futures
    uid_path = UidPathUtil()
    # Collect all file_info objects first (for progress bar sizing)
    file_infos = []
    for root in volume_roots:
        file_infos.extend(scan_files_on_volume(root, uid_path))
    total_files = len(file_infos)
    if total_files == 0:
        return
    with tqdm(total=total_files, desc=f"Analyzing {table}") as pbar:
        def process_file(file_info):
            persist_file_metadata(db_path, table, file_info)
            logging.info(f"Indexed: {file_info['uid']}:{file_info['relative_path']} size={file_info['size']} mtime={file_info['last_modified']}")
            pbar.update(1)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(process_file, file_infos))
