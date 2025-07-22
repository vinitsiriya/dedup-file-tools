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
    job_dir = os.path.dirname(db_path)
    checksum_db_path = os.path.join(job_dir, 'checksum-cache.db')
    checksum_conn = sqlite3.connect(checksum_db_path)
    uid_path_util = None
    try:
        from dedup_file_tools_commons.utils.uidpath import UidPathUtil
        uid_path_util = UidPathUtil()
    except ImportError:
        pass
    checksum_cache2 = ChecksumCache2(uid_path_util)

    # Build sets of checksums for left and right pools
    def get_checksum(uid, rel_path):
        cur = checksum_conn.cursor()
        cur.execute('SELECT checksum FROM checksum_cache WHERE uid=? AND relative_path=? AND is_valid=1', (uid, rel_path))
        row = cur.fetchone()
        return row[0] if row else None

    left_checksums = {}
    for (uid, rel_path) in left_map:
        csum = get_checksum(uid, rel_path)
        if csum:
            left_checksums[(uid, rel_path)] = csum

    right_checksums = {}
    for (uid, rel_path) in right_map:
        csum = get_checksum(uid, rel_path)
        if csum:
            right_checksums[(uid, rel_path)] = csum

    # Find identical files by checksum
    identical = []
    left_csum_to_info = {v: (k, left_map[k][0], left_map[k][1]) for k, v in left_checksums.items()}
    right_csum_to_info = {v: (k, right_map[k][0], right_map[k][1]) for k, v in right_checksums.items()}
    for csum in set(left_csum_to_info.keys()) & set(right_csum_to_info.keys()):
        (left_uid_rel, left_mtime, left_size) = left_csum_to_info[csum]
        (right_uid_rel, right_mtime, right_size) = right_csum_to_info[csum]
        # Insert using left uid/rel_path as key, but include both left/right info and checksum
        identical.append((left_uid_rel[0], left_uid_rel[1], left_mtime, left_size, right_mtime, right_size, csum))

    # Find missing files by checksum
    missing_from_right = []
    for (uid, rel_path), csum in left_checksums.items():
        if csum not in right_csum_to_info:
            missing_from_right.append((uid, rel_path, left_map[(uid, rel_path)][0], left_map[(uid, rel_path)][1]))

    missing_from_left = []
    for (uid, rel_path), csum in right_checksums.items():
        if csum not in left_csum_to_info:
            missing_from_left.append((uid, rel_path, right_map[(uid, rel_path)][0], right_map[(uid, rel_path)][1]))

    # Find differing files by checksum (same rel_path, different checksum)
    different = []
    for (uid, rel_path) in set(left_map.keys()) & set(right_map.keys()):
        csum_left = left_checksums.get((uid, rel_path))
        csum_right = right_checksums.get((uid, rel_path))
        if csum_left and csum_right and csum_left != csum_right:
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
    # Always insert missing from right
    batches = [missing_from_right[i:i+batch_size] for i in range(0, len(missing_from_right), batch_size)]
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futs = [executor.submit(insert_batch, 'compare_results_right_missing', batch, 'uid,relative_path,last_modified,size') for batch in batches]
        if not no_progress:
            for _ in tqdm(as_completed(futs), total=len(futs), desc="Missing from right", unit="batch"):
                pass
        else:
            for _ in as_completed(futs):
                pass

    # Always insert missing from left
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
