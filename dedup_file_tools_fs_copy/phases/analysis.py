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
    try:
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
        logging.info(f"[AGENT][ANALYZE] Persisted metadata: {file_info}")
    except Exception as e:
        logging.exception(f"Error persisting file metadata: {file_info} - {e}")

def scan_file_on_directory(directory_root, uid_path: UidPathUtil):
    # Always use UidPath.convert_path for every file, even in test directories
    mountpoint = directory_root if os.path.isdir(directory_root) else uid_path.get_mount_point_from_volume_id(uid_path.get_volume_id_from_path(directory_root))
    if not mountpoint:
        logging.error(f"Mount point not found for directory {directory_root}")
        return []
    logging.info(f"[AGENT][ANALYZE] Scanning directory: {mountpoint}")
    # Sequentially list all file paths
    all_files = list(Path(mountpoint).rglob("*"))
    file_paths = [f for f in all_files if f.is_file()]
    # Parallelize all expensive file info extraction (stat, UID, etc.)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    file_infos = []
    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(_extract_file_info, file, uid_path) for file in file_paths]
            with tqdm(total=len(file_paths), desc=f"Scanning {mountpoint}", unit="file", miniters=max(1, len(file_paths)//100)) as pbar:
                for f in as_completed(futures):
                    info = f.result()
                    if info:
                        file_infos.append(info)
                    pbar.update(1)
        logging.info(f"[AGENT][ANALYZE] Scanned {len(file_infos)} files in directory: {mountpoint}")
    except Exception as e:
        logging.exception(f"[AGENT][ANALYZE] Error scanning directory {mountpoint}: {e}")
    return file_infos

def _extract_file_info(file, uid_path):
    try:
        uid_path_obj = uid_path.convert_path(str(file))
        uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
        if uid is None:
            logging.error(f"[AGENT][ANALYZE] Could not determine UID for file {file}")
            return None
        stat = file.stat()
        logging.info(f"[AGENT][ANALYZE] Indexed: {file}")
        return {
            'uid': uid,
            'relative_path': rel,
            'size': stat.st_size,
            'last_modified': int(stat.st_mtime)
        }
    except Exception as e:
        logging.error(f"[AGENT][ANALYZE] Error extracting info for {file}: {e}")
        return None

def analyze_directories(db_path, directory_roots, table):
    import concurrent.futures
    uid_path = UidPathUtil()
    logging.info(f"[AGENT][ANALYZE] Starting analysis for directories: {directory_roots} into table: {table}")
    # Step 1: Collect all file paths (file names) in a single array, sequentially
    all_file_paths = []
    for root in directory_roots:
        # Directly scan the root directory, no uid_path or mount point logic
        if not os.path.exists(root):
            logging.error(f"[AGENT][ANALYZE] Directory not found: {root}")
            continue
        all_files = list(Path(root).rglob("*"))
        all_file_paths.extend([f for f in all_files if f.is_file()])
    total_files = len(all_file_paths)
    if total_files == 0:
        logging.warning("[AGENT][ANALYZE] No files found to analyze.")
        return
    # Step 2: Extract file info in parallel
    from concurrent.futures import ThreadPoolExecutor, as_completed
    all_file_infos = []
    try:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(_extract_file_info, file, uid_path) for file in all_file_paths]
            with tqdm(total=total_files, desc=f"Analyzing {table}", miniters=max(100, total_files // 100)) as pbar:
                for f in as_completed(futures):
                    info = f.result()
                    if info:
                        all_file_infos.append(info)
                    pbar.update(1)
        logging.info(f"[AGENT][ANALYZE] Extracted info for {len(all_file_infos)} files.")
    except Exception as e:
        logging.exception(f"[AGENT][ANALYZE] Error extracting file info: {e}")
    # Step 3: Batch persist metadata in parallel, with less frequent tqdm updates
    batch_size = max(100, total_files // 100)
    try:
        with tqdm(total=total_files, desc=f"Persisting {table}", miniters=batch_size) as pbar:
            def process_file(file_info):
                persist_file_metadata(db_path, table, file_info)
                logging.info(f"Indexed: {file_info['uid']}:{file_info['relative_path']} size={file_info['size']} mtime={file_info['last_modified']}")
            with ThreadPoolExecutor() as executor:
                for i in range(0, total_files, batch_size):
                    batch = all_file_infos[i:i+batch_size]
                    list(executor.map(process_file, batch))
                    pbar.update(len(batch))
        logging.info(f"[AGENT][ANALYZE] Persisted metadata for {len(all_file_infos)} files.")
    except Exception as e:
        logging.exception(f"[AGENT][ANALYZE] Error persisting file metadata: {e}")
