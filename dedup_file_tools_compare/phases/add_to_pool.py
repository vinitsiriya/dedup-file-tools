import logging


import os
import sqlite3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def _file_info(fpath, directory):
    stat = fpath.stat()
    if os.name == 'nt':
        uid = fpath.drive.upper()
    else:
        uid = '/'  # TODO: use real mount point/uidpath abstraction
    rel_path = str(fpath.relative_to(directory))
    return (uid, rel_path, int(stat.st_mtime), stat.st_size)

def _insert_batch(db_path, table, batch):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executemany(f'''
        INSERT OR REPLACE INTO {table} (uid, relative_path, last_modified, size)
        VALUES (?, ?, ?, ?)
    ''', batch)
    conn.commit()
    conn.close()

def add_directory_to_pool(db_path, directory, table, threads=4, batch_size=1000, show_progress=True):
    logging.info(f"[COMPARE][POOL] Scanning directory {directory} for files to add to {table}")
    directory = Path(directory)
    all_files = []
    if show_progress:
        for root, dirs, files in tqdm(os.walk(directory), desc="Collecting files", unit="dir", leave=False):
            for fname in files:
                all_files.append(Path(root) / fname)
    else:
        for root, dirs, files in os.walk(directory):
            for fname in files:
                all_files.append(Path(root) / fname)
    total = len(all_files)
    logging.info(f"[COMPARE][POOL] Found {total} files in {directory}")
    batches = [all_files[i:i+batch_size] for i in range(0, total, batch_size)]

    def process_batch(batch):
        return [_file_info(f, directory) for f in batch]

    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        if show_progress:
            for f in tqdm(as_completed(futures), total=len(futures), desc="Scanning files", unit="batch"):
                results.extend(f.result())
        else:
            for f in as_completed(futures):
                results.extend(f.result())

    # Insert in DB in batches
    for i in range(0, len(results), batch_size):
        _insert_batch(db_path, table, results[i:i+batch_size])
    logging.info(f"[COMPARE][POOL] Added {len(results)} files to {table} in {db_path}")
