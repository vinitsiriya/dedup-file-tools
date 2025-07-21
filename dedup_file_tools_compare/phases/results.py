
import sqlite3
import csv
import json
import os

def show_result(db_path, summary=False, full_report=False, output=None, show='all', use_normal_paths=False):
    import logging
    logging.info(f"[COMPARE][RESULTS] Loading results from {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Load results
    cur.execute('SELECT COUNT(*) FROM compare_results_right_missing')
    missing_right = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM compare_results_left_missing')
    missing_left = cur.fetchone()[0]
    # Identical and different
    try:
        cur.execute('SELECT COUNT(*) FROM compare_results_identical')
        identical_count = cur.fetchone()[0]
    except sqlite3.OperationalError:
        identical_count = 0
    try:
        cur.execute('SELECT COUNT(*) FROM compare_results_different')
        different_count = cur.fetchone()[0]
    except sqlite3.OperationalError:
        different_count = 0

    if summary:
        print(f"Summary:")
        print(f"  Missing from right: {missing_right}")
        print(f"  Missing from left: {missing_left}")
        print(f"  Identical files: {identical_count}")
        print(f"  Differing files: {different_count}")
        logging.info(f"[COMPARE][RESULTS] Summary: missing_right={missing_right}, missing_left={missing_left}, identical={identical_count}, different={different_count}")
        conn.close()
        return

    # Full report - split missing_left and missing_right
    import datetime
    results_left = []
    results_right = []
    results_identical = []
    results_different = []
    if show in ('all', 'unique-left'):
        cur.execute('SELECT uid, relative_path, last_modified, size FROM compare_results_left_missing')
        left_missing_rows = cur.fetchall()
        for row in left_missing_rows:
            results_left.append({'category': 'missing_left', 'uid': row[0], 'relative_path': row[1], 'last_modified': row[2], 'size': row[3]})
    if show in ('all', 'unique-right'):
        cur.execute('SELECT uid, relative_path, last_modified, size FROM compare_results_right_missing')
        right_missing_rows = cur.fetchall()
        for row in right_missing_rows:
            results_right.append({'category': 'missing_right', 'uid': row[0], 'relative_path': row[1], 'last_modified': row[2], 'size': row[3]})
    if show in ('all', 'identical'):
        try:
            cur.execute('SELECT uid, relative_path, last_modified_left, size_left, last_modified_right, size_right, checksum FROM compare_results_identical')
            for row in cur.fetchall():
                results_identical.append({'category': 'identical', 'uid': row[0], 'relative_path': row[1], 'last_modified_left': row[2], 'size_left': row[3], 'last_modified_right': row[4], 'size_right': row[5], 'checksum': row[6]})
        except sqlite3.OperationalError:
            pass
    if show in ('all', 'different'):
        try:
            cur.execute('SELECT uid, relative_path, last_modified_left, size_left, last_modified_right, size_right, checksum_left, checksum_right FROM compare_results_different')
            for row in cur.fetchall():
                results_different.append({'category': 'different', 'uid': row[0], 'relative_path': row[1], 'last_modified_left': row[2], 'size_left': row[3], 'last_modified_right': row[4], 'size_right': row[5], 'checksum_left': row[6], 'checksum_right': row[7]})
        except sqlite3.OperationalError:
            pass

    # Ensure every row has uid and relative_path for portability
    for r in results_left + results_right + results_identical + results_different:
        if 'uid' not in r:
            r['uid'] = ''
        if 'relative_path' not in r:
            r['relative_path'] = ''

    # If use_normal_paths, reconstruct absolute path and add as 'absolute_path' column
    if use_normal_paths:
        from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
        uid_util = UidPathUtil()
        for r in results_left + results_right + results_identical + results_different:
            try:
                abs_path = None
                if r['uid'] and r['relative_path']:
                    abs_path = uid_util.reconstruct_path(UidPath(r['uid'], r['relative_path']))
                r['absolute_path'] = str(abs_path) if abs_path else ''
            except Exception as e:
                r['absolute_path'] = ''

    # Output logic: always write CSVs in a timestamped directory
    if output:
        # Determine base directory and create timestamped subdir
        base_dir = os.path.dirname(output)
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = os.path.join(base_dir, f'reports_{ts}')
        os.makedirs(out_dir, exist_ok=True)
        # Write missing_left.csv
        if results_left:
            left_csv = os.path.join(out_dir, 'missing_left.csv')
            fieldnames = list({k for r in results_left for k in r.keys()})
            with open(left_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_left)
            print(f"Wrote missing_left results to {left_csv}")
            logging.info(f"[COMPARE][RESULTS] Wrote missing_left CSV to {left_csv}")
        # Write missing_right.csv
        if results_right:
            right_csv = os.path.join(out_dir, 'missing_right.csv')
            fieldnames = list({k for r in results_right for k in r.keys()})
            with open(right_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_right)
            print(f"Wrote missing_right results to {right_csv}")
            logging.info(f"[COMPARE][RESULTS] Wrote missing_right CSV to {right_csv}")
        # Write identical.csv
        if results_identical:
            identical_csv = os.path.join(out_dir, 'identical.csv')
            fieldnames = list({k for r in results_identical for k in r.keys()})
            with open(identical_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_identical)
            print(f"Wrote identical results to {identical_csv}")
            logging.info(f"[COMPARE][RESULTS] Wrote identical CSV to {identical_csv}")
        # Write different.csv
        if results_different:
            different_csv = os.path.join(out_dir, 'different.csv')
            fieldnames = list({k for r in results_different for k in r.keys()})
            with open(different_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results_different)
            print(f"Wrote different results to {different_csv}")
            logging.info(f"[COMPARE][RESULTS] Wrote different CSV to {different_csv}")
    else:
        for r in results_left + results_right + results_identical + results_different:
            print(r)
        logging.info(f"[COMPARE][RESULTS] Printed {len(results_left) + len(results_right) + len(results_identical) + len(results_different)} results to console")
    conn.close()
