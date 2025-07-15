"""
File: fs-copy-tool/main.py
Description: Main orchestration script for Non-Redundant Media File Copy Tool
"""
import argparse
import logging
import os
import sys
import sqlite3
from pathlib import Path
from fs_copy_tool.db import init_db
from fs_copy_tool.phases.analysis import analyze_volumes
from fs_copy_tool.phases.copy import copy_files
from fs_copy_tool.phases.verify import shallow_verify_files, deep_verify_files
from fs_copy_tool.utils.uidpath import UidPath
from fs_copy_tool.utils.checksum_cache import ChecksumCache

def init_job_dir(job_dir):
    os.makedirs(job_dir, exist_ok=True)
    db_path = os.path.join(job_dir, 'copytool.db')
    init_db(db_path)
    # Optionally create log, planning, and state files here
    # ...
    print(f"Initialized job directory at {job_dir} with database {db_path}")


def get_db_path_from_job_dir(job_dir):
    return os.path.join(job_dir, 'copytool.db')

def add_file_to_db(db_path, file_path):
    from pathlib import Path
    import sys
    from fs_copy_tool.utils.uidpath import UidPath
    file = Path(file_path)
    if not file.is_file():
        print(f"Error: {file_path} is not a file.", file=sys.stderr)
        sys.exit(1)
    uid_path = UidPath()
    uid, rel = uid_path.convert_path(str(file))
    if uid is None:
        print(f"Error: Could not determine UID for {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        stat = file.stat()
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO source_files (uid, relative_path, size, last_modified)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(uid, relative_path) DO UPDATE SET
                    size=excluded.size,
                    last_modified=excluded.last_modified
            """, (uid, rel, stat.st_size, int(stat.st_mtime)))
            conn.commit()
        print(f"Added file: {file_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error adding file: {file_path}\n{e}", file=sys.stderr)
        sys.exit(1)

def add_source_to_db(db_path, src_dir):
    uid_path = UidPath()
    src = Path(src_dir)
    if not src.is_dir():
        print(f"Error: {src_dir} is not a directory.")
        return
    count = 0
    for file in src.rglob("*"):
        if file.is_file():
            uid, rel = uid_path.convert_path(str(file))
            if uid is None:
                print(f"Error: Could not determine UID for {file}", file=sys.stderr)
                continue
            # Print debug info for each file added
            print(f"ADD_SOURCE DEBUG: uid={uid}, rel={rel}, file={file}", file=sys.stderr)
            stat = file.stat()
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO source_files (uid, relative_path, size, last_modified)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(uid, relative_path) DO UPDATE SET
                        size=excluded.size,
                        last_modified=excluded.last_modified
                """, (uid, rel, stat.st_size, int(stat.st_mtime)))
                conn.commit()
            count += 1
    print(f"Added {count} files from directory: {src_dir}")

def list_files_in_db(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM source_files ORDER BY uid, relative_path")
        rows = cur.fetchall()
        for row in rows:
            print(f"{row[0]} | {row[1]} | size: {row[2]} | mtime: {row[3]}")
    print(f"Total files: {len(rows)}")

def remove_file_from_db(db_path, file_path):
    file = Path(file_path)
    mount_id = str(file.parent)
    rel = file.name
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM source_files WHERE uid=? AND relative_path=?", (mount_id, rel))
        conn.commit()
    print(f"Removed file: {file_path}")

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Non-Redundant Media File Copy Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize a new job directory')
    parser_init.add_argument('--job-dir', required=True, help='Path to job directory')

    # Import checksums command (simplified, only from checksum_cache)
    parser_import = subparsers.add_parser('import-checksums', help='Import checksums from the checksum_cache table of another compatible database')
    parser_import.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_import.add_argument('--other-db', required=True, help='Path to other compatible SQLite database (must have checksum_cache table)')

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
    parser_shallow_verify = subparsers.add_parser('verify', help='Shallow or deep verify: check existence, size, last_modified, or checksums')
    parser_shallow_verify.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_shallow_verify.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_shallow_verify.add_argument('--dst', nargs='+', help='Destination volume root(s)')
    parser_shallow_verify.add_argument('--stage', choices=['shallow', 'deep'], default='shallow', help='Verification stage: shallow (default) or deep')

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

    # Add file command
    parser_add_file = subparsers.add_parser('add-file', help='Add a single file to the job state/database')
    parser_add_file.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_add_file.add_argument('--file', required=True, help='Path to the file to add')

    # Add source command (recursive add)
    parser_add_source = subparsers.add_parser('add-source', help='Recursively add all files from a directory to the job state/database')
    parser_add_source.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_add_source.add_argument('--src', required=True, help='Source directory to add')

    # List files command
    parser_list_files = subparsers.add_parser('list-files', help='List all files currently in the job state/database')
    parser_list_files.add_argument('--job-dir', required=True, help='Path to job directory')

    # Remove file command
    parser_remove_file = subparsers.add_parser('remove-file', help='Remove a file from the job state/database')
    parser_remove_file.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_remove_file.add_argument('--file', required=True, help='Path to the file to remove')

    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    return run_main_command(parsed_args)

def handle_init(args):
    init_job_dir(args.job_dir)
    return 0

def handle_analyze(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    init_db(db_path)
    if args.src:
        analyze_volumes(db_path, args.src, 'source_files')
    if args.dst:
        analyze_volumes(db_path, args.dst, 'destination_files')
    return 0

def handle_copy(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    init_db(db_path)
    copy_files(db_path, args.src, args.dst, threads=args.threads)
    return 0

def handle_verify(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    if args.stage == 'shallow':
        shallow_verify_files(db_path, args.src, args.dst)
    else:
        deep_verify_files(db_path, args.src, args.dst)
    return 0

def handle_resume(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    init_db(db_path)
    copy_files(db_path, args.src, args.dst)
    return 0

def handle_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM source_files WHERE copy_status='done'")
        done = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM source_files WHERE copy_status='pending' OR copy_status IS NULL")
        pending = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM source_files WHERE copy_status='error'")
        error = cur.fetchone()[0]
        print(f"Done: {done}, Pending: {pending}, Error: {error}")
    return 0

def handle_log(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        print('Copied files (destination_files):')
        cur.execute("SELECT uid, relative_path, size, last_modified, copy_status FROM destination_files WHERE copy_status='done'")
        for row in cur.fetchall():
            print(f"{row[0]} | {row[1]} | size: {row[2]} | mtime: {row[3]} | status: {row[4]}")
        print('---')
        print('Errors (source_files):')
        cur.execute("SELECT uid, relative_path, copy_status, error_message FROM source_files WHERE copy_status='error'")
        for row in cur.fetchall():
            print(f"{row[0]} | {row[1]} | status: {row[2]} | error: {row[3]}")
    return 0

def handle_deep_verify(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    deep_verify_files(db_path, args.src, args.dst)
    return 0

def handle_verify_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
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
    return 0

def handle_deep_verify_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        print('Deep Verification Results:')
        cur.execute('''
            SELECT relative_path, verify_status, verify_error, expected_checksum, src_checksum, dst_checksum, timestamp
            FROM verification_deep_results
            WHERE timestamp = (SELECT MAX(timestamp) FROM verification_deep_results vd2 WHERE vd2.relative_path = verification_deep_results.relative_path)
            ORDER BY relative_path
        ''')
        for row in cur.fetchall():
            print(f"{row[0]} | status: {row[1]} | error: {row[2]} | expected: {row[3]} | src: {row[4]} | dst: {row[5]} | ts: {row[6]}")
    return 0

def handle_add_file(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    add_file_to_db(db_path, args.file)
    return 0

def handle_add_source(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    add_source_to_db(db_path, args.src)
    return 0

def handle_list_files(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    list_files_in_db(db_path)
    return 0

def handle_remove_file(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    remove_file_from_db(db_path, args.file)
    return 0

def handle_checksum(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    init_db(db_path)
    uid_path = UidPath()
    checksum_cache = ChecksumCache(db_path, uid_path)
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT uid, relative_path, size, last_modified FROM {args.table}")
        rows = cur.fetchall()
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    def process_row(row):
        uid, rel_path, size, last_modified = row
        file_path = uid_path.reconstruct_path(uid, rel_path)
        if not file_path or not file_path.exists():
            return None
        checksum = checksum_cache.get_or_compute(str(file_path))
        return True if checksum else None
    with tqdm(total=len(rows), desc=f"Checksumming {args.table}") as pbar:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(process_row, row) for row in rows]
            for f in as_completed(futures):
                pbar.update(1)
    return 0

def handle_import_checksums(args):
    db_path = get_db_path_from_job_dir(args.job_dir)
    other_db_path = args.other_db
    # Validate schema of other_db
    with sqlite3.connect(other_db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checksum_cache'")
        if not cur.fetchone():
            print(f"Error: The other database does not have a checksum_cache table.", file=sys.stderr)
            sys.exit(1)
        # Import all rows from other checksum_cache
        cur.execute("SELECT uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid FROM checksum_cache")
        rows = cur.fetchall()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for row in rows:
            cur.execute("""
                INSERT OR REPLACE INTO checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
        conn.commit()
    print(f"Imported {len(rows)} checksums from {other_db_path} into checksum_cache.")
    return 0

def run_main_command(args):
    if args.command == 'init':
        return handle_init(args)
    elif args.command == 'import-checksums':
        return handle_import_checksums(args)
    elif args.command == 'analyze':
        return handle_analyze(args)
    elif args.command == 'checksum':
        return handle_checksum(args)
    elif args.command == 'copy':
        return handle_copy(args)
    elif args.command == 'verify':
        return handle_verify(args)
    elif args.command == 'resume':
        return handle_resume(args)
    elif args.command == 'status':
        return handle_status(args)
    elif args.command == 'log':
        return handle_log(args)
    elif args.command == 'deep-verify':
        return handle_deep_verify(args)
    elif args.command == 'verify-status':
        return handle_verify_status(args)
    elif args.command == 'deep-verify-status':
        return handle_deep_verify_status(args)
    elif args.command == 'add-file':
        return handle_add_file(args)
    elif args.command == 'add-source':
        return handle_add_source(args)
    elif args.command == 'list-files':
        return handle_list_files(args)
    elif args.command == 'remove-file':
        return handle_remove_file(args)
    else:
        print("No command specified or unknown command.")
        return 1

if __name__ == "__main__":
    main()
