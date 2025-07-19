import os
import shutil
import time
from pathlib import Path
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def move_duplicates(db_path, dupes_folder, removal_folder, threads=4):
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, checksum, status FROM dedup_move_plan WHERE status='planned'")
        rows = cur.fetchall()
    import logging
    from dedup_file_tools_commons.utils.uidpath import UidPath, UidPathUtil
    uid_path_util = UidPathUtil()
    from concurrent.futures import ThreadPoolExecutor
    from tqdm import tqdm
    from collections import deque
    def move_one(args):
        uid, rel_path, checksum, status = args
        src_path = uid_path_util.reconstruct_path(UidPath(uid, rel_path))
        dst_path = Path(removal_folder) / Path(rel_path).name
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            if os.stat(src_path).st_dev == os.stat(dst_path.parent).st_dev:
                Path(src_path).rename(dst_path)
                move_type = 'fast-move'
            else:
                shutil.copy2(src_path, dst_path)
                Path(src_path).unlink()
                move_type = 'copy-delete'
            moved_at = int(time.time())
            with RobustSqliteConn(db_path).connect() as conn2:
                cur2 = conn2.cursor()
                cur2.execute("""
                    UPDATE dedup_move_plan SET status='moved', error_message=NULL, moved_at=?, updated_at=? WHERE uid=? AND relative_path=?
                """, (moved_at, moved_at, uid, rel_path))
                cur2.execute("""
                    INSERT INTO dedup_move_history (uid, relative_path, attempted_at, action, result, error_message)
                    VALUES (?, ?, ?, ?, ?, NULL)
                """, (uid, rel_path, moved_at, 'move', move_type))
                conn2.commit()
            return (uid, rel_path, None)
        except Exception as e:
            with RobustSqliteConn(db_path).connect() as conn2:
                cur2 = conn2.cursor()
                cur2.execute("""
                    UPDATE dedup_move_plan SET status='error', error_message=?, updated_at=? WHERE uid=? AND relative_path=?
                """, (str(e), int(time.time()), uid, rel_path))
                cur2.execute("""
                    INSERT INTO dedup_move_history (uid, relative_path, attempted_at, action, result, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (uid, rel_path, int(time.time()), 'move', 'error', str(e)))
                conn2.commit()
            return (uid, rel_path, str(e))
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = deque()
        row_iter = iter(rows)
        for _ in range(min(threads * 2, len(rows))):
            try:
                row = next(row_iter)
                futures.append((executor.submit(move_one, row), row))
            except StopIteration:
                break
        pbar = tqdm(total=len(rows), desc="Moving duplicates", unit="file")
        completed = 0
        while futures:
            future, row = futures.popleft()
            try:
                uid, rel_path, err = future.result()
                if err:
                    logging.error(f"Move error for {uid}:{rel_path}: {err}")
            except Exception as e:
                logging.error(f"Thread failed for {row[0]}:{row[1]}: {e}")
            completed += 1
            pbar.update(1)
            try:
                next_row = next(row_iter)
                futures.append((executor.submit(move_one, next_row), next_row))
            except StopIteration:
                pass
        pbar.close()
