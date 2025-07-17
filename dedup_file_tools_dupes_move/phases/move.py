"""
Phase: Move

dedup_file_tools_dupes_move/phases/move.py

Description:
    Implements the move phase for duplicate files. Moves duplicates to the target location(s) using the most efficient method: atomic rename (os.rename/Path.rename) for same-device moves, or copy+delete for cross-device moves. Logs and tracks status for auditability and resumability. Integrates with the shared database and checksum cache, preserves relative structure, and ensures only true duplicates are moved.
"""

import os
import shutil
from pathlib import Path
import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache

def move_file(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    if not src_path.exists():
        raise FileNotFoundError(f"Source file not found: {src}")
    try:
        if os.stat(src_path).st_dev == os.stat(dst_path.parent).st_dev:
            src_path.rename(dst_path)
            logging.info(f"[MOVE] Fast move (rename): {src} -> {dst}")
            return 'fast-move'
        else:
            shutil.copy2(src_path, dst_path)
            src_path.unlink()
            logging.info(f"[MOVE] Copy+delete: {src} -> {dst}")
            return 'copy-delete'
    except Exception as e:
        logging.error(f"[MOVE][ERROR] {src} -> {dst}: {e}")
        raise

def mark_move_status(db_path, uid, rel_path, status, error_message=None):
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS move_status (
                uid TEXT,
                relative_path TEXT,
                status TEXT, -- 'pending', 'in_progress', 'done', 'error'
                last_move_attempt INTEGER,
                error_message TEXT,
                PRIMARY KEY (uid, relative_path)
            )
        """)
        cur.execute("""
            INSERT INTO move_status (uid, relative_path, status, last_move_attempt, error_message)
            VALUES (?, ?, ?, strftime('%s','now'), ?)
            ON CONFLICT(uid, relative_path) DO UPDATE SET
                status=excluded.status,
                last_move_attempt=excluded.last_move_attempt,
                error_message=excluded.error_message
        """, (uid, rel_path, status, error_message))
        conn.commit()

def get_pending_moves(db_path):
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT uid, relative_path, size, last_modified, checksum, target_path
            FROM duplicate_candidates
            LEFT JOIN move_status ms ON duplicate_candidates.uid = ms.uid AND duplicate_candidates.relative_path = ms.relative_path
            WHERE (ms.status IS NULL OR ms.status='pending' OR ms.status='error' OR ms.status='in_progress')
        """)
        return cur.fetchall()

def move_duplicates(db_path, dest_root, threads=4, dry_run=False):
    """
    Move all queued duplicate files to dest_root, preserving relative structure. Only move if destination does not already have the file (by checksum). Supports dry-run and resumability.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm
    uid_path = UidPathUtil()
    def conn_factory():
        return RobustSqliteConn(db_path).connect()
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    pending = get_pending_moves(db_path)
    if not pending:
        logging.info("No pending duplicate moves.")
        return
    def process_move(args):
        uid, rel_path, size, last_modified, checksum, target_path = args
        src_path = uid_path.reconstruct_path(UidPath(uid, rel_path))
        dst_path = Path(target_path)
        # Check if destination already has this checksum
        if dst_path.exists():
            dst_checksum = checksum_cache.get_or_compute_with_invalidation(str(dst_path))
            if dst_checksum == checksum:
                mark_move_status(db_path, uid, rel_path, 'done', 'Already present at destination')
                logging.info(f"[MOVE][SKIP] Destination already has file with same checksum: {dst_path}")
                return 'skipped'
        if dry_run:
            logging.info(f"[MOVE][DRY-RUN] Would move {src_path} -> {dst_path}")
            mark_move_status(db_path, uid, rel_path, 'pending', 'Dry-run: not moved')
            return 'dry-run'
        mark_move_status(db_path, uid, rel_path, 'in_progress')
        try:
            result = move_file(src_path, dst_path)
            mark_move_status(db_path, uid, rel_path, 'done')
            return result
        except Exception as e:
            mark_move_status(db_path, uid, rel_path, 'error', str(e))
            return 'error'
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(process_move, args) for args in pending]
        with tqdm(total=len(futures), desc="Moving duplicates") as pbar:
            for f in as_completed(futures):
                try:
                    f.result()
                finally:
                    pbar.update(1)
