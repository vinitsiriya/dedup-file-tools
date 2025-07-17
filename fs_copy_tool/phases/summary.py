import os
import csv
from fs_copy_tool.utils.robust_sqlite import RobustSqliteConn
import logging
from pathlib import Path

def summary_phase(db_path, job_dir):
    """
    Prints a summary of what has happened, where the logs are, and generates a CSV report of errors and not-done files.
    """
    print("\n==== SUMMARY PHASE ====")
    print(f"Job directory: {job_dir}")
    log_path = os.path.join(job_dir, 'fs_copy_tool.log')
    if os.path.exists(log_path):
        print(f"Log file: {log_path}")
    else:
        print("Log file not found in job directory.")

    conn = RobustSqliteConn(db_path).connect()
    cur = conn.cursor()
    # Collect files with errors or not done from copy_status table
    cur.execute("""
        SELECT s.uid, s.relative_path, cs.status as copy_status, cs.error_message
        FROM source_files s
        JOIN copy_status cs ON s.uid = cs.uid AND s.relative_path = cs.relative_path
        WHERE cs.status != 'done'
    """)
    rows = cur.fetchall()
    if not rows:
        print("All files copied successfully. No errors or pending files.")
    else:
        print(f"{len(rows)} file(s) with errors or not done. See CSV report.")
    # Write CSV
    csv_path = os.path.join(job_dir, 'summary_report.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['uid', 'relative_path', 'copy_status', 'error_message'])
        for row in rows:
            writer.writerow(row)
    print(f"CSV report generated: {csv_path}")
    conn.close()
    print("=======================\n")
