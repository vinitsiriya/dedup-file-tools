"""
Phase: Analysis

dedup_file_tools_dupes_move/phases/analysis.py

Description:
    Scans the source directory, computes checksums using the shared cache, and populates the database with duplicate candidates. Only files with duplicate checksums are queued for moving. Uses UidPath for all file references.
"""

import os
from pathlib import Path
import logging
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def find_and_queue_duplicates(db_path, src_root, threads=4):
    """
    Scan src_root recursively, compute checksums, and populate duplicate_candidates table.
    Only files with duplicate checksums are queued for moving.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm
    uid_path = UidPathUtil()
    def conn_factory():
        return RobustSqliteConn(db_path).connect()
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    # Step 1: Scan all files
    files = [str(p) for p in Path(src_root).rglob("*") if Path(p).is_file()]
    # Step 2: Compute checksums in parallel
    checksums = {}
    def compute(path):
        chksum = checksum_cache.get_or_compute_with_invalidation(path)
        return (path, chksum)
    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = list(tqdm(executor.map(compute, files), total=len(files), desc="Checksumming"))
    # Step 3: Group by checksum
    checksum_to_files = {}
    for path, chksum in results:
        if not chksum:
            continue
        checksum_to_files.setdefault(chksum, []).append(path)
    # Step 4: For each group with >1 file, queue all but one for moving
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS duplicate_candidates (
                uid TEXT,
                relative_path TEXT,
                size INTEGER,
                last_modified INTEGER,
                checksum TEXT,
                target_path TEXT,
                PRIMARY KEY (uid, relative_path)
            )
        """)
        conn.commit()
        for chksum, paths in checksum_to_files.items():
            if len(paths) < 2:
                continue
            # Pick one to keep (the first), others to move
            keeper = paths[0]
            for path in paths[1:]:
                uid_path_obj = uid_path.convert_path(path)
                uid, rel_path = uid_path_obj.uid, uid_path_obj.relative_path
                stat = Path(path).stat()
                # Compute target path (e.g., move to a 'dupes' folder under src_root)
                target_path = str(Path(src_root) / "dupes" / rel_path)
                cur.execute("""
                    INSERT OR REPLACE INTO duplicate_candidates (uid, relative_path, size, last_modified, checksum, target_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uid, rel_path, stat.st_size, int(stat.st_mtime), chksum, target_path))
        conn.commit()
    logging.info("Duplicate candidates queued for move.")
