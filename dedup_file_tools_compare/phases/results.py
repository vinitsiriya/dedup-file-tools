
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

    # Full report
    results = []
    if show in ('all', 'unique-left'):
        cur.execute('SELECT uid, relative_path, last_modified, size FROM compare_results_left_missing')
        left_missing_rows = cur.fetchall()
        print('DEBUG: compare_results_left_missing rows:', left_missing_rows)
        for row in left_missing_rows:
            results.append({'category': 'missing_left', 'uid': row[0], 'relative_path': row[1], 'last_modified': row[2], 'size': row[3]})
    if show in ('all', 'unique-right'):
        cur.execute('SELECT uid, relative_path, last_modified, size FROM compare_results_right_missing')
        right_missing_rows = cur.fetchall()
        print('DEBUG: compare_results_right_missing rows:', right_missing_rows)
        for row in right_missing_rows:
            results.append({'category': 'missing_right', 'uid': row[0], 'relative_path': row[1], 'last_modified': row[2], 'size': row[3]})
    if show in ('all', 'identical'):
        try:
            cur.execute('SELECT uid, relative_path, last_modified_left, size_left, last_modified_right, size_right, checksum FROM compare_results_identical')
            for row in cur.fetchall():
                results.append({'category': 'identical', 'uid': row[0], 'relative_path': row[1], 'last_modified_left': row[2], 'size_left': row[3], 'last_modified_right': row[4], 'size_right': row[5], 'checksum': row[6]})
        except sqlite3.OperationalError:
            pass
    if show in ('all', 'different'):
        try:
            cur.execute('SELECT uid, relative_path, last_modified_left, size_left, last_modified_right, size_right, checksum_left, checksum_right FROM compare_results_different')
            for row in cur.fetchall():
                results.append({'category': 'different', 'uid': row[0], 'relative_path': row[1], 'last_modified_left': row[2], 'size_left': row[3], 'last_modified_right': row[4], 'size_right': row[5], 'checksum_left': row[6], 'checksum_right': row[7]})
        except sqlite3.OperationalError:
            pass

    # Ensure every row has uid and relative_path for portability
    for r in results:
        if 'uid' not in r:
            r['uid'] = ''
        if 'relative_path' not in r:
            r['relative_path'] = ''

    # If use_normal_paths, reconstruct absolute path and add as 'absolute_path' column
    if use_normal_paths:
        from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
        uid_util = UidPathUtil()
        for r in results:
            try:
                abs_path = None
                if r['uid'] and r['relative_path']:
                    abs_path = uid_util.reconstruct_path(UidPath(r['uid'], r['relative_path']))
                r['absolute_path'] = str(abs_path) if abs_path else ''
            except Exception as e:
                r['absolute_path'] = ''

    if output:
        ext = os.path.splitext(output)[1].lower()
        if ext == '.csv':
            # Use superset of all fields
            fieldnames = set()
            for r in results:
                fieldnames.update(r.keys())
            fieldnames = list(fieldnames)
            with open(output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Wrote results to {output}")
            logging.info(f"[COMPARE][RESULTS] Wrote CSV results to {output}")
        elif ext == '.json':
            with open(output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"Wrote results to {output}")
            logging.info(f"[COMPARE][RESULTS] Wrote JSON results to {output}")
        else:
            print(f"Unknown output file extension: {ext}")
            logging.warning(f"[COMPARE][RESULTS] Unknown output file extension: {ext}")
    else:
        for r in results:
            print(r)
        logging.info(f"[COMPARE][RESULTS] Printed {len(results)} results to console")
    conn.close()
