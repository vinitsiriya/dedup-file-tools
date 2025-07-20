from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sqlite3

def run_checksum_table(db_path, checksum_db_path, table, threads=4, no_progress=False):
    """
    Compute or update checksums for all files in the given table (source_files or destination_files).
    """
    uid_path = UidPathUtil()
    checksum_cache = ChecksumCache2(uid_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT uid, relative_path, size, last_modified FROM {table}")
        rows = cur.fetchall()

    # Batch processing: split rows into batches of at least 5000
    min_batch_size = 5000
    total_rows = len(rows)
    batch_size = max(min_batch_size, total_rows // threads) if total_rows > 0 else min_batch_size
    batches = [rows[i:i+batch_size] for i in range(0, total_rows, batch_size)]

    def process_batch(batch):
        with RobustSqliteConn(checksum_db_path).connect() as checksum_conn:
            local_count = 0
            for row in batch:
                uid, rel_path, size, last_modified = row
                uid_path_obj = UidPath(uid, rel_path)
                file_path = uid_path.reconstruct_path(uid_path_obj)
                logging.info(f"[run_checksum_table] Processing: uid={uid}, rel_path={rel_path}, resolved_path={file_path}")
                if not file_path or not file_path.exists():
                    logging.info(f"[run_checksum_table] File not found or does not exist: {file_path}")
                    continue
                logging.info(f"[run_checksum_table] Calling get_or_compute_with_invalidation for {file_path}")
                checksum = checksum_cache.get_or_compute_with_invalidation(checksum_conn, str(file_path))
                logging.info(f"[run_checksum_table] Checksum for {file_path}: {checksum}")
                local_count += 1
                if not no_progress:
                    progress_iter.update(1)
            return local_count

    progress_iter = tqdm(total=total_rows, desc=f"Checksumming {table}") if not no_progress else None
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(executor.map(process_batch, batches))
    if not no_progress and progress_iter:
        progress_iter.close()
    return 0
