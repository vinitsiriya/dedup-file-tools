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

    parser_copy = subparsers.add_parser('copy', help='Copy files from source to destination')
    parser_copy.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_copy.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_copy.add_argument('--dst', nargs='+', help='Destination volume root(s)')

    # Resume command
    parser_resume = subparsers.add_parser('resume', help='Resume incomplete or failed operations')
    parser_resume.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_resume.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_resume.add_argument('--dst', nargs='+', help='Destination volume root(s)')

    # Status command
    parser_status = subparsers.add_parser('status', help='Show job progress and statistics')
    parser_status.add_argument('--job-dir', required=True, help='Path to job directory')

    # Log/Audit command
    parser_log = subparsers.add_parser('log', help='Show job log or audit trail')
    parser_log.add_argument('--job-dir', required=True, help='Path to job directory')

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
        update_checksums(db_path, args.table)
        return
    elif args.command == 'copy':
        db_path = get_db_path_from_job_dir(args.job_dir)
        init_db(db_path)
        copy_files(db_path, args.src, args.dst)
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
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
