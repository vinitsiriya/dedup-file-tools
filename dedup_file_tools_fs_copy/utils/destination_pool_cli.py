
import logging
from pathlib import Path
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from .destination_pool import DestinationPoolIndex

def add_to_destination_index_pool(db_path, dst_root):
    """
    Recursively scan dst_root and add/update all files in the destination pool index.
    """
    uid_path = UidPathUtil()
    dst_root = Path(dst_root)
    logging.info(f"[AGENT][POOL] Adding files from {dst_root}")
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor
    all_files = []
    notify_every = 10000
    count = 0
    logging.info(f"[AGENT][POOL] Starting file discovery in {dst_root}")
    for f in dst_root.rglob("*"):
        if f.is_file():
            all_files.append(f)
            count += 1
            if count % notify_every == 0:
                logging.info(f"[AGENT][POOL] Discovered {count} files so far in {dst_root}")
    total_files = len(all_files)
    logging.info(f"[AGENT][POOL] File discovery complete: {total_files} files found in {dst_root}")
    min_batch_size = 5000
    batch_size = max(min_batch_size, total_files // 100) if total_files > 0 else min_batch_size
    from threading import Lock
    batches = [all_files[i:i+batch_size] for i in range(0, total_files, batch_size)]
    processed = 0
    pbar_lock = Lock()
    logging.info(f"[AGENT][POOL] Starting tqdm progress bar for indexing {total_files} files from {dst_root}")

    # Use a single DB connection for all checksum operations
    pool = DestinationPoolIndex(uid_path)
    checksum_cache = ChecksumCache2(uid_path)
    from tqdm import tqdm
    with tqdm(total=total_files, desc=f"Indexing destination pool from {dst_root}", unit="file") as pbar:
        def process_batch(batch):
            # Each thread opens its own connection for its batch
            with RobustSqliteConn(db_path).connect() as conn:
                for path in batch:
                    stat = path.stat()
                    # Optionally, you can use checksum_cache here for checksum-related logic if needed
                    pool.add_or_update_file(conn, str(path), stat.st_size, int(stat.st_mtime))
                    logging.info(f"[AGENT][POOL] Added/updated file in destination pool index: {path}")
                    with pbar_lock:
                        pbar.update(1)
        with ThreadPoolExecutor() as executor:
            list(executor.map(process_batch, batches))
    logging.info(f"[AGENT][POOL] Batch add/update complete: {total_files} files processed in destination pool index from {dst_root}")
