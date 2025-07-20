from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
from tqdm import tqdm
import logging
import sys

def run_import_checksums(db_path, checksum_db_path, other_db_path):
    # Validate schema of other_db
    with RobustSqliteConn(other_db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checksum_cache'")
        if not cur.fetchone():
            logging.error(f"Error: The other database does not have a checksum_cache table.")
            sys.exit(1)
        # Import all rows from other checksum_cache
        cur.execute("SELECT uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid FROM checksum_cache")
        rows = cur.fetchall()
    # Insert into attached checksum DB in batches
    logging.info(f"[AGENT][MAIN] Rows to import from other DB: {len(rows)} rows")
    min_batch_size = 5000
    total_rows = len(rows)
    batch_size = max(min_batch_size, total_rows // 10) if total_rows > 0 else min_batch_size
    batches = [rows[i:i+batch_size] for i in range(0, total_rows, batch_size)]
    conn = connect_with_attached_checksum_db(db_path, checksum_db_path)
    try:
        cur = conn.cursor()
        with tqdm(total=total_rows, desc="Importing checksums", unit="row") as pbar:
            for batch in batches:
                for row in batch:
                    cur.execute("""
                        INSERT OR REPLACE INTO checksumdb.checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, row)
                    pbar.update(1)
                conn.commit()
        # Log all rows in checksum_cache after import
        cur.execute("SELECT COUNT(*) FROM checksumdb.checksum_cache")
        count = cur.fetchone()[0]
        logging.info(f"[AGENT][MAIN] All rows in main job's checksum_cache after import: {count} rows")
    finally:
        conn.close()
    logging.info(f"[AGENT][MAIN] Imported {len(rows)} checksums from {other_db_path} into checksum_cache.")
    return 0
