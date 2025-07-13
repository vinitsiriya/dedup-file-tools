"""
File: fs-copy-tool/main.py
Description: Main orchestration script for Non-Redundant Media File Copy Tool
"""
import argparse
import logging
import os
import sys
from fs_copy_tool.db import init_db
from fs_copy_tool.phases.analysis import analyze_volumes
from fs_copy_tool.phases.checksum import update_checksums, import_checksums_from_old_db
from fs_copy_tool.phases.copy import copy_files
from fs_copy_tool.phases.verify import shallow_verify_files, deep_verify_files

def init_job_dir(job_dir):
    os.makedirs(job_dir, exist_ok=True)
    db_path = os.path.join(job_dir, 'copytool.db')
    init_db(db_path)
    # Optionally create log, planning, and state files here
    # ...
    print(f"Initialized job directory at {job_dir} with database {db_path}")


def get_db_path_from_job_dir(job_dir):
    return os.path.join(job_dir, 'copytool.db')

def main():
    parser = argparse.ArgumentParser(description="Non-Redundant Media File Copy Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize a new job directory')
    parser_init.add_argument('--job-dir', required=True, help='Path to job directory')

    # Import checksums command
    parser_import = subparsers.add_parser('import-checksums', help='Import checksums from an old SQLite database')
    parser_import.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_import.add_argument('--old-db', required=True, help='Path to old SQLite database')
    parser_import.add_argument('--table', choices=['source_files', 'destination_files'], default='source_files', help='Table to import into')

    # Analyze, checksum, copy, etc. commands
    parser_analyze = subparsers.add_parser('analyze', help='Analyze source/destination volumes')
    parser_analyze.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_analyze.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_analyze.add_argument('--dst', nargs='+', help='Destination volume root(s)')

    parser_checksum = subparsers.add_parser('checksum', help='Update checksums for files')
    parser_checksum.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_checksum.add_argument('--table', choices=['source_files', 'destination_files'], required=True)
    parser_checksum.add_argument('--threads', type=int, default=4, help='Number of threads for checksum phase (default: 4)')
    parser_checksum.add_argument('--no-progress', action='store_true', help='Disable progress bar')

    parser_copy = subparsers.add_parser('copy', help='Copy files from source to destination. Skips already completed files and resumes incomplete jobs by default.')
    parser_copy.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_copy.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_copy.add_argument('--dst', nargs='+', help='Destination volume root(s)')
    parser_copy.add_argument('--threads', type=int, default=4, help='Number of threads for copy phase (default: 4)')
    parser_copy.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    parser_copy.add_argument('--resume', action='store_true', default=True, help='[Default] Resume incomplete jobs by skipping already completed files. This is always enabled.')

    # Resume command
    parser_resume = subparsers.add_parser('resume', help='Alias for copy: resumes incomplete or failed operations (skips completed files).')
    parser_resume.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_resume.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_resume.add_argument('--dst', nargs='+', help='Destination volume root(s)')
    parser_resume.add_argument('--threads', type=int, default=4, help='Number of threads for copy phase (default: 4)')
    parser_resume.add_argument('--no-progress', action='store_true', help='Disable progress bar')

    # Status command
    parser_status = subparsers.add_parser('status', help='Show job progress and statistics')
    parser_status.add_argument('--job-dir', required=True, help='Path to job directory')

    # Log/Audit command
    parser_log = subparsers.add_parser('log', help='Show job log or audit trail')
    parser_log.add_argument('--job-dir', required=True, help='Path to job directory')

    # Shallow verify command (basic attributes)
    parser_shallow_verify = subparsers.add_parser('verify', help='Shallow verify: check existence, size, last_modified')
    parser_shallow_verify.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_shallow_verify.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_shallow_verify.add_argument('--dst', nargs='+', help='Destination volume root(s)')

    # Deep verify command (checksums)
    parser_deep_verify = subparsers.add_parser('deep-verify', help='Deep verify: compare checksums between source and destination')
    parser_deep_verify.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_deep_verify.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_deep_verify.add_argument('--dst', nargs='+', help='Destination volume root(s)')

    # Shallow verify status command
    parser_shallow_status = subparsers.add_parser('verify-status', help='Show a summary of the latest shallow verification results for each file')
    parser_shallow_status.add_argument('--job-dir', required=True, help='Path to job directory')

    # Deep verify status command
    parser_deep_status = subparsers.add_parser('deep-verify-status', help='Show a summary of the latest deep verification results for each file')
    parser_deep_status.add_argument('--job-dir', required=True, help='Path to job directory')

    # Shallow verify status summary (short)
    parser_shallow_status_summary = subparsers.add_parser('verify-status-summary', help='Show a summary (short) of the latest shallow verification results for each file')
    parser_shallow_status_summary.add_argument('--job-dir', required=True, help='Path to job directory')

    # Shallow verify status full (detailed)
    parser_shallow_status_full = subparsers.add_parser('verify-status-full', help='Show all shallow verification results (full history)')
    parser_shallow_status_full.add_argument('--job-dir', required=True, help='Path to job directory')

    # Deep verify status summary (short)
    parser_deep_status_summary = subparsers.add_parser('deep-verify-status-summary', help='Show a summary (short) of the latest deep verification results for each file')
    parser_deep_status_summary.add_argument('--job-dir', required=True, help='Path to job directory')

    # Deep verify status full (detailed)
    parser_deep_status_full = subparsers.add_parser('deep-verify-status-full', help='Show all deep verification results (full history)')
    parser_deep_status_full.add_argument('--job-dir', required=True, help='Path to job directory')

    args = parser.parse_args()

    if args.command == 'init':
        init_job_dir(args.job_dir)
        return
    elif args.command == 'import-checksums':
        db_path = get_db_path_from_job_dir(args.job_dir)
        updates = import_checksums_from_old_db(db_path, args.old_db, args.table)
        print(f"Imported {updates} checksums from {args.old_db} into {db_path} [{args.table}]")
        return
    elif args.command == 'analyze':
        db_path = get_db_path_from_job_dir(args.job_dir)
        init_db(db_path)
        if args.src:
            analyze_volumes(db_path, args.src, 'source_files')
        if args.dst:
            analyze_volumes(db_path, args.dst, 'destination_files')
        return
    elif args.command == 'checksum':
        db_path = get_db_path_from_job_dir(args.job_dir)
        init_db(db_path)
        update_checksums(db_path, args.table, threads=args.threads)
        return
    elif args.command == 'copy':
        db_path = get_db_path_from_job_dir(args.job_dir)
        init_db(db_path)
        copy_files(db_path, args.src, args.dst, threads=args.threads)
        return
    elif args.command == 'resume':
        db_path = get_db_path_from_job_dir(args.job_dir)
        init_db(db_path)
        # Resume: retry pending/error files in copy phase
        copy_files(db_path, args.src, args.dst)
        return
    elif args.command == 'status':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM source_files WHERE copy_status='done'")
            done = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM source_files WHERE copy_status='pending' OR copy_status IS NULL")
            pending = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM source_files WHERE copy_status='error'")
            error = cur.fetchone()[0]
            print(f"Done: {done}, Pending: {pending}, Error: {error}")
        return
    elif args.command == 'log':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT uid, relative_path, copy_status, error_message FROM source_files WHERE copy_status IS NOT NULL")
            for row in cur.fetchall():
                print(row)
        return
    elif args.command == 'verify':
        db_path = get_db_path_from_job_dir(args.job_dir)
        shallow_verify_files(db_path, args.src, args.dst)
        return
    elif args.command == 'deep-verify':
        db_path = get_db_path_from_job_dir(args.job_dir)
        deep_verify_files(db_path, args.src, args.dst)
        return
    elif args.command == 'verify-status':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            print('Shallow Verification Results:')
            cur.execute('''
                SELECT relative_path, verify_status, verify_error, expected_size, actual_size, expected_last_modified, actual_last_modified
                FROM verification_shallow_results
                WHERE timestamp = (SELECT MAX(timestamp) FROM verification_shallow_results vs2 WHERE vs2.relative_path = verification_shallow_results.relative_path)
                ORDER BY relative_path
            ''')
            for row in cur.fetchall():
                print(f"{row[0]} | status: {row[1]} | error: {row[2]} | size: {row[4]}/{row[3]} | mtime: {row[6]}/{row[5]}")
        return
    elif args.command == 'deep-verify-status':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            print('Deep Verification Results:')
            cur.execute('''
                SELECT relative_path, verify_status, verify_error, expected_checksum, src_checksum, dst_checksum
                FROM verification_deep_results
                WHERE timestamp = (SELECT MAX(timestamp) FROM verification_deep_results vd2 WHERE vd2.relative_path = verification_deep_results.relative_path)
                ORDER BY relative_path
            ''')
            for row in cur.fetchall():
                print(f"{row[0]} | status: {row[1]} | error: {row[2]} | expected: {row[3]} | src: {row[4]} | dst: {row[5]}")
        return
    elif args.command == 'verify-status-summary':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            print('Shallow Verification Results (Summary):')
            cur.execute('''
                SELECT relative_path, verify_status, verify_error, expected_size, actual_size, expected_last_modified, actual_last_modified
                FROM verification_shallow_results
                WHERE timestamp = (SELECT MAX(timestamp) FROM verification_shallow_results vs2 WHERE vs2.relative_path = verification_shallow_results.relative_path)
                ORDER BY relative_path
            ''')
            for row in cur.fetchall():
                print(f"{row[0]} | status: {row[1]} | error: {row[2]} | size: {row[4]}/{row[3]} | mtime: {row[6]}/{row[5]}")
        return
    elif args.command == 'verify-status-full':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            print('Shallow Verification Results (Full History):')
            cur.execute('''
                SELECT relative_path, verify_status, verify_error, expected_size, actual_size, expected_last_modified, actual_last_modified, timestamp
                FROM verification_shallow_results
                ORDER BY relative_path, timestamp DESC
            ''')
            for row in cur.fetchall():
                print(f"{row[0]} | status: {row[1]} | error: {row[2]} | size: {row[4]}/{row[3]} | mtime: {row[6]}/{row[5]} | ts: {row[7]}")
        return
    elif args.command == 'deep-verify-status-summary':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            print('Deep Verification Results (Summary):')
            cur.execute('''
                SELECT relative_path, verify_status, verify_error, expected_checksum, src_checksum, dst_checksum
                FROM verification_deep_results
                WHERE timestamp = (SELECT MAX(timestamp) FROM verification_deep_results vd2 WHERE vd2.relative_path = verification_deep_results.relative_path)
                ORDER BY relative_path
            ''')
            for row in cur.fetchall():
                print(f"{row[0]} | status: {row[1]} | error: {row[2]} | expected: {row[3]} | src: {row[4]} | dst: {row[5]}")
        return
    elif args.command == 'deep-verify-status-full':
        db_path = get_db_path_from_job_dir(args.job_dir)
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            print('Deep Verification Results (Full History):')
            cur.execute('''
                SELECT relative_path, verify_status, verify_error, expected_checksum, src_checksum, dst_checksum, timestamp
                FROM verification_deep_results
                ORDER BY relative_path, timestamp DESC
            ''')
            for row in cur.fetchall():
                print(f"{row[0]} | status: {row[1]} | error: {row[2]} | expected: {row[3]} | src: {row[4]} | dst: {row[5]} | ts: {row[6]}")
        return
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
