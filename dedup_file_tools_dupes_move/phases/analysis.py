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
    # Step 2: Compute checksums in parallel
    def compute(path):
        chksum = checksum_cache.get_or_compute_with_invalidation(path)
        return (path, chksum)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(tqdm(executor.map(compute, files), total=len(files), desc="Checksumming"))
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
            cur.execute("""
                INSERT OR REPLACE INTO dedup_files_pool (uid, relative_path, size, last_modified, checksum, scanned_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (uid, rel_path, stat.st_size, int(stat.st_mtime), chksum, now))
        conn.commit()
    # Step 4: Group by checksum
    checksum_to_files = {}
    for path, chksum in results:
        if not chksum:
            continue
        checksum_to_files.setdefault(chksum, []).append(path)
    # Step 5: For each group with >1 file, pick a keeper, queue others in dedup_move_plan
    with connect_with_attached_checksum_db(db_path, checksum_db_path) as conn:
        cur = conn.cursor()
        for chksum, paths in checksum_to_files.items():
            if len(paths) < 2:
                continue
            # Pick one to keep (the first), others to move
            keeper_path = paths[0]
            keeper_uid_path = uid_path.convert_path(keeper_path)
            keeper_uid, keeper_rel_path = keeper_uid_path.uid, keeper_uid_path.relative_path
            # Insert keeper with is_keeper=1
            cur.execute("""
                INSERT OR REPLACE INTO dedup_move_plan (uid, relative_path, checksum, move_to_uid, move_to_rel_path, status, planned_at, is_keeper)
                VALUES (?, ?, ?, NULL, NULL, ?, ?, 1)
            """, (keeper_uid, keeper_rel_path, chksum, 'keeper', now))
            # Insert others with is_keeper=0, status='planned', move_to_* = keeper
            for path in paths[1:]:
                uid_path_obj = uid_path.convert_path(path)
                uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
                cur.execute("""
                    INSERT OR REPLACE INTO dedup_move_plan (uid, relative_path, checksum, move_to_uid, move_to_rel_path, status, planned_at, is_keeper)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """, (uid, rel_path, chksum, keeper_uid, keeper_rel_path, 'planned', now))
        conn.commit()
    logging.info("Duplicate move plan queued for all duplicate groups.")
