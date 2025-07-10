"""
File: fs-copy-tool/phases/checksum.py
Description: Checksum sync phase logic
"""
import sqlite3
import logging
from fs_copy_tool.utils.uidpath import UidPath
from fs_copy_tool.utils.fileops import compute_sha256
from pathlib import Path

def update_checksums(db_path, table):
    uid_path = UidPath()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT uid, relative_path FROM {table} WHERE checksum IS NULL OR checksum_stale=1")
        rows = cur.fetchall()
        for uid, rel_path in rows:
            mountpoint = uid_path.get_mount_point_from_volume_id(uid)
            if not mountpoint:
                logging.error(f"Mount point not found for volume {uid}")
                continue
            file_path = Path(mountpoint) / rel_path
            checksum = compute_sha256(file_path)
            if checksum:
                cur.execute(f"""
                    UPDATE {table} SET checksum=?, checksum_stale=0 WHERE uid=? AND relative_path=?
                """, (checksum, uid, rel_path))
                conn.commit()
                logging.info(f"Checksum updated: {uid}:{rel_path}")

def import_checksums_from_old_db(new_db_path, old_db_path, table):
    """
    Import checksum values from old_db_path into new_db_path for the given table (source_files or destination_files).
    Only updates rows where uid and relative_path match and checksum is not already set.
    """
    with sqlite3.connect(old_db_path) as old_conn, sqlite3.connect(new_db_path) as new_conn:
        old_cur = old_conn.cursor()
        new_cur = new_conn.cursor()
        old_cur.execute(f"SELECT uid, relative_path, checksum FROM {table} WHERE checksum IS NOT NULL")
        updates = 0
        for uid, rel_path, checksum in old_cur.fetchall():
            # Only update if checksum is not already set in new db
            new_cur.execute(f"SELECT checksum FROM {table} WHERE uid=? AND relative_path=?", (uid, rel_path))
            row = new_cur.fetchone()
            if row and (row[0] is None or row[0] == ""):
                new_cur.execute(f"UPDATE {table} SET checksum=?, checksum_stale=0 WHERE uid=? AND relative_path=?", (checksum, uid, rel_path))
                updates += 1
        new_conn.commit()
    return updates
