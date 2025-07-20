
"""
File: dedup_file_tools_fs_copy/phases/summary.py
Phase: Summary

Description:
    Implements the summary phase for the Non-Redundant Media File Copy Tool. This module generates a summary report after the copy phase, including a CSV file listing files that encountered errors or were not copied. It also prints job and log file locations for user reference.

Key Features:
    - Summarizes the results of the copy operation
    - Reports the location of log files and job directory
    - Generates a CSV report of files with errors or incomplete status
    - Designed for use in both CLI and agent-driven workflows

Usage:
    Invoked as the final phase in the workflow to provide a clear summary and error report for auditing and troubleshooting.
"""

import os
import csv
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def summary_phase(db_path, job_dir):
    """
    Prints a summary of what has happened, where the logs are, and generates a CSV report of errors and not-done files.
    """
    import logging
    logger = logging.getLogger()
    logger.info("==== SUMMARY PHASE ====")
    logger.info(f"Job directory: {job_dir}")
    log_path = os.path.join(job_dir, 'dedup_file_tools_fs_copy.log')
    if os.path.exists(log_path):
        logger.info(f"Log file: {log_path}")
    else:
        logger.warning("Log file not found in job directory.")
    try:
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
            logger.info("All files copied successfully. No errors or pending files.")
        else:
            logger.warning(f"{len(rows)} file(s) with errors or not done. See CSV report.")
        # Write CSV
        csv_path = os.path.join(job_dir, 'summary_report.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['uid', 'relative_path', 'copy_status', 'error_message'])
            for row in rows:
                writer.writerow(row)
        logger.info(f"CSV report generated: {csv_path}")
        conn.close()
    except Exception as e:
        logger.exception(f"Exception in summary_phase: {e}")
    logger.info("=======================\n")
