import csv
import os
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def summary_report(db_path, job_dir):
    csv_path = os.path.join(job_dir, 'dedup_move_summary.csv')
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dedup_move_plan")
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        # Count by status
        cur.execute("SELECT status, COUNT(*) FROM dedup_move_plan GROUP BY status")
        status_counts = dict(cur.fetchall())
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(colnames)
        writer.writerows(rows)
    print("\n==== DEDUP MOVE SUMMARY ====")
    print(f"Job directory: {job_dir}")
    print(f"Summary CSV written to: {csv_path}")
    log_path = os.path.join(job_dir, 'logs')
    print(f"Log files directory: {log_path}")
    print("\nStatus counts:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
