import logging

import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2

def find_missing_files(db_path, by='checksum', threads=4, no_progress=False, left=False, right=False, both=False):
    logging.info(f"[COMPARE][COMPARE] Starting comparison for {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()


    # Clear previous results
    cur.execute('DELETE FROM compare_results_left_missing')
    cur.execute('DELETE FROM compare_results_right_missing')
    cur.execute('DROP TABLE IF EXISTS compare_results_identical')
    cur.execute('DROP TABLE IF EXISTS compare_results_different')
    cur.execute('''CREATE TABLE IF NOT EXISTS compare_results_identical (
        uid TEXT, relative_path TEXT, last_modified_left INTEGER, size_left INTEGER, last_modified_right INTEGER, size_right INTEGER, checksum TEXT, PRIMARY KEY (uid, relative_path)
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS compare_results_different (
        uid TEXT, relative_path TEXT, last_modified_left INTEGER, size_left INTEGER, last_modified_right INTEGER, size_right INTEGER, checksum_left TEXT, checksum_right TEXT, PRIMARY KEY (uid, relative_path)
    )''')
    conn.commit()


    # Load left and right pool files
    cur.execute('SELECT uid, relative_path, last_modified, size FROM left_pool_files')
    left_files = cur.fetchall()
    cur.execute('SELECT uid, relative_path, last_modified, size FROM right_pool_files')
    right_files = cur.fetchall()
    logging.info(f"[COMPARE][COMPARE] Loaded {len(left_files)} left files and {len(right_files)} right files")

    left_map = {(uid, rel_path): (last_modified, size) for uid, rel_path, last_modified, size in left_files}
    right_map = {(uid, rel_path): (last_modified, size) for uid, rel_path, last_modified, size in right_files}
    left_set = set(left_map.keys())
    right_set = set(right_map.keys())

    # Find missing from right (present in left, not in right)
    missing_from_right = [(uid, rel_path, left_map[(uid, rel_path)][0], left_map[(uid, rel_path)][1]) for (uid, rel_path) in left_set - right_set]
    # Find missing from left (present in right, not in left)
    missing_from_left = [(uid, rel_path, right_map[(uid, rel_path)][0], right_map[(uid, rel_path)][1]) for (uid, rel_path) in right_set - left_set]

    logging.info(f"[COMPARE][COMPARE] Missing from right: {len(missing_from_right)}, missing from left: {len(missing_from_left)}")

    # For files present in both, compare checksums
    both = left_set & right_set
    # Load checksums from shared checksum DB (assume checksum-cache.db in job_dir)
    job_dir = os.path.dirname(db_path)
    checksum_db_path = os.path.join(job_dir, 'checksum-cache.db')
    checksum_conn = sqlite3.connect(checksum_db_path)
    # Use ChecksumCache2 for generic pool checks
    uid_path_util = None
    try:
        from dedup_file_tools_commons.utils.uidpath import UidPathUtil
        uid_path_util = UidPathUtil()
    except ImportError:
        pass
    checksum_cache2 = ChecksumCache2(uid_path_util)

    logging.info(f"[COMPARE][COMPARE] Comparing {len(both)} files present in both pools")

    def get_checksum(uid, rel_path):
        cur = checksum_conn.cursor()
        cur.execute('SELECT checksum FROM checksum_cache WHERE uid=? AND relative_path=? AND is_valid=1', (uid, rel_path))
        row = cur.fetchone()
        return row[0] if row else None

    identical = []
    different = []
    for (uid, rel_path) in tqdm(both, desc="Comparing checksums", unit="file"):
        csum_left = get_checksum(uid, rel_path)
        csum_right = get_checksum(uid, rel_path)
        # Example: check if this checksum exists in left or right pool using exists_at_pool
        exists_in_left = checksum_cache2.exists_at_pool(checksum_conn, 'left_pool_files', csum_left) if csum_left else False
        exists_in_right = checksum_cache2.exists_at_pool(checksum_conn, 'right_pool_files', csum_right) if csum_right else False
        # In this design, both sides use the same checksum DB, so csum_left == csum_right
        if csum_left and csum_right:
            if csum_left == csum_right:
                identical.append((uid, rel_path, left_map[(uid, rel_path)][0], left_map[(uid, rel_path)][1], right_map[(uid, rel_path)][0], right_map[(uid, rel_path)][1], csum_left))
            else:
                different.append((uid, rel_path, left_map[(uid, rel_path)][0], left_map[(uid, rel_path)][1], right_map[(uid, rel_path)][0], right_map[(uid, rel_path)][1], csum_left, csum_right))
        else:
            # If checksum missing, treat as different
            different.append((uid, rel_path, left_map[(uid, rel_path)][0], left_map[(uid, rel_path)][1], right_map[(uid, rel_path)][0], right_map[(uid, rel_path)][1], csum_left, csum_right))

    checksum_conn.close()

    # Insert results in parallel batches
    def insert_batch(table, batch, fields):
        c = sqlite3.connect(db_path)
        q = f"INSERT OR REPLACE INTO {table} ({fields}) VALUES ({','.join(['?']*len(fields.split(',')))})"
        c.executemany(q, batch)
        c.commit()
        c.close()

    batch_size = 1000
    # Missing from right
    if right or both:
        batches = [missing_from_right[i:i+batch_size] for i in range(0, len(missing_from_right), batch_size)]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futs = [executor.submit(insert_batch, 'compare_results_right_missing', batch, 'uid,relative_path,last_modified,size') for batch in batches]
            if not no_progress:
                for _ in tqdm(as_completed(futs), total=len(futs), desc="Missing from right", unit="batch"):
                    pass
            else:
                for _ in as_completed(futs):
                    pass
    # Missing from left
    if left or both:
        batches = [missing_from_left[i:i+batch_size] for i in range(0, len(missing_from_left), batch_size)]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futs = [executor.submit(insert_batch, 'compare_results_left_missing', batch, 'uid,relative_path,last_modified,size') for batch in batches]
            if not no_progress:
                for _ in tqdm(as_completed(futs), total=len(futs), desc="Missing from left", unit="batch"):
                    pass
            else:
                for _ in as_completed(futs):
                    pass
    # Identical
    if both or (not left and not right):
        batches = [identical[i:i+batch_size] for i in range(0, len(identical), batch_size)]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futs = [executor.submit(insert_batch, 'compare_results_identical', batch, 'uid,relative_path,last_modified_left,size_left,last_modified_right,size_right,checksum') for batch in batches]
            if not no_progress:
                for _ in tqdm(as_completed(futs), total=len(futs), desc="Identical files", unit="batch"):
                    pass
            else:
                for _ in as_completed(futs):
                    pass
    # Different
    if both or (not left and not right):
        batches = [different[i:i+batch_size] for i in range(0, len(different), batch_size)]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futs = [executor.submit(insert_batch, 'compare_results_different', batch, 'uid,relative_path,last_modified_left,size_left,last_modified_right,size_right,checksum_left,checksum_right') for batch in batches]
            if not no_progress:
                for _ in tqdm(as_completed(futs), total=len(futs), desc="Differing files", unit="batch"):
                    pass
            else:
                for _ in as_completed(futs):
                    pass

    print(f"Missing from right: {len(missing_from_right)}")
    print(f"Missing from left: {len(missing_from_left)}")
    print(f"Identical files: {len(identical)}")
    print(f"Differing files: {len(different)}")
    logging.info(f"[COMPARE][COMPARE] Identical: {len(identical)}, Different: {len(different)}")
    conn.close()
