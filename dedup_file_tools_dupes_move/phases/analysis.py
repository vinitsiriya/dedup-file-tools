import os
from pathlib import Path
import logging
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def find_and_queue_duplicates(db_path, src_root, threads=4):
    """
    Scan src_root recursively, compute checksums, persist all file metadata to dedup_files_pool,
    group by checksum, and queue all but one file per group in dedup_move_plan.
    """
    from concurrent.futures import ThreadPoolExecutor
    from tqdm import tqdm
    import time
    from dedup_file_tools_commons.utils.paths import get_checksum_db_path
    from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
    uid_path = UidPathUtil()
    checksum_db_path = get_checksum_db_path(os.path.dirname(db_path))
    def conn_factory():
        return connect_with_attached_checksum_db(db_path, checksum_db_path)
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    # Step 1: Scan all files
    files = [str(p) for p in Path(src_root).rglob("*") if Path(p).is_file()]
    # Step 2: Compute checksums in parallel, robust to errors and hangs
    import logging
    from concurrent.futures import as_completed
    import time
    def compute(path):
        start = time.time()
        try:
            chksum = checksum_cache.get_or_compute_with_invalidation(path)
            elapsed = time.time() - start
            if elapsed > 30:
                logging.warning(f"Slow checksum: {path} took {elapsed:.1f}s")
            return (path, chksum, None)
        except Exception as e:
            logging.error(f"Checksum failed for {path}: {e}")
            return (path, None, str(e))
    from collections import deque
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = deque()
        file_iter = iter(files)
        # Prime the pool
        for _ in range(min(threads * 2, len(files))):
            try:
                path = next(file_iter)
                futures.append((executor.submit(compute, path), path))
            except StopIteration:
                break
        pbar = tqdm(total=len(files), desc="Checksumming", unit="file")
        completed = 0
        while futures:
            future, path = futures.popleft()
            try:
                path2, chksum, err = future.result()
                if err:
                    logging.error(f"Checksum error for {path2}: {err}")
                results.append((path2, chksum))
            except Exception as e:
                logging.error(f"Thread failed for {path}: {e}")
                results.append((path, None))
            completed += 1
            pbar.update(1)
            # Submit next file if any remain
            try:
                next_path = next(file_iter)
                futures.append((executor.submit(compute, next_path), next_path))
            except StopIteration:
                pass
        pbar.close()
    # Step 3: Persist all file metadata to dedup_files_pool
    now = int(time.time())
    with connect_with_attached_checksum_db(db_path, checksum_db_path) as conn:
        cur = conn.cursor()
        for path, chksum in results:
            if not chksum:
                continue
            stat = Path(path).stat()
            uid_path_obj = uid_path.convert_path(path)
            uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
            # Compute pool_base_path as src_root (absolute)
            pool_base_path = os.path.abspath(src_root)
            cur.execute("""
                INSERT OR REPLACE INTO dedup_files_pool (uid, relative_path, size, last_modified, checksum, scanned_at, pool_base_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (uid, rel_path, stat.st_size, int(stat.st_mtime), chksum, now, pool_base_path))
        conn.commit()
    # Step 4: Group by checksum globally across all files in dedup_files_pool
    with connect_with_attached_checksum_db(db_path, checksum_db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, checksum FROM dedup_files_pool WHERE checksum IS NOT NULL")
        all_files = cur.fetchall()
        checksum_to_files = {}
        for uid, rel_path, chksum in all_files:
            if not chksum:
                continue
            checksum_to_files.setdefault(chksum, []).append((uid, rel_path))
        # Clear existing move plan (optional: only for planned, not moved)
        cur.execute("DELETE FROM dedup_move_plan WHERE status='planned'")
        for chksum, file_tuples in checksum_to_files.items():
            if len(file_tuples) < 2:
                continue
            # Pick one to keep (the first), others to move
            keeper_uid, keeper_rel_path = file_tuples[0]
            # Insert keeper with is_keeper=1
            cur.execute("""
                INSERT OR REPLACE INTO dedup_move_plan (uid, relative_path, checksum, move_to_uid, move_to_rel_path, status, planned_at, is_keeper)
                VALUES (?, ?, ?, NULL, NULL, ?, ?, 1)
            """, (keeper_uid, keeper_rel_path, chksum, 'keeper', now))
            # Insert others with is_keeper=0, status='planned', move_to_* = keeper
            for uid, rel_path in file_tuples[1:]:
                cur.execute("""
                    INSERT OR REPLACE INTO dedup_move_plan (uid, relative_path, checksum, move_to_uid, move_to_rel_path, status, planned_at, is_keeper)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """, (uid, rel_path, chksum, keeper_uid, keeper_rel_path, 'planned', now))
        conn.commit()
    logging.info("Duplicate move plan queued for all duplicate groups.")
