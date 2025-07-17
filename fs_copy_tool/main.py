def handle_add_to_destination_index_pool(args):
    from fs_copy_tool.utils.destination_pool_cli import add_to_destination_index_pool
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    add_to_destination_index_pool(db_path, args.dst)
    return 0
"""
File: fs-copy-tool/main.py
Description: Main orchestration script for Non-Redundant Media File Copy Tool
"""

import argparse
import logging
import sys
import os
log_level = None
for i, arg in enumerate(sys.argv):
    if arg == '--log-level' and i + 1 < len(sys.argv):
        log_level = sys.argv[i + 1]
        break
from fs_copy_tool.utils.logging_config import setup_logging
setup_logging(log_level=log_level)
import os
import sys
from fs_copy_tool.utils.robust_sqlite import RobustSqliteConn
from pathlib import Path
from fs_copy_tool.db import init_db
from fs_copy_tool.phases.analysis import analyze_volumes
from fs_copy_tool.phases.copy import copy_files
from fs_copy_tool.phases.verify import shallow_verify_files, deep_verify_files
from fs_copy_tool.utils.uidpath import UidPathUtil, UidPath
from fs_copy_tool.utils.checksum_cache import ChecksumCache
from fs_copy_tool.utils.logging_config import setup_logging

def init_job_dir(job_dir, job_name, checksum_db=None):
    from fs_copy_tool.db import init_db, init_checksum_db
    os.makedirs(job_dir, exist_ok=True)
    db_path = os.path.join(job_dir, f'{job_name}.db')
    checksum_db_path = checksum_db or os.path.join(job_dir, 'checksum-cache.db')
    init_db(db_path)
    if not os.path.exists(checksum_db_path):
        init_checksum_db(checksum_db_path)
    logging.info(f"Initialized job directory at {job_dir} with database {db_path} and checksum DB {checksum_db_path}")

def get_db_path_from_job_dir(job_dir, job_name):
    return os.path.join(job_dir, f'{job_name}.db')

def get_checksum_db_path(job_dir, checksum_db=None):
    if checksum_db:
        return checksum_db
    return os.path.join(job_dir, 'checksum-cache.db')

# Centralized DB connection with attached checksum DB
def connect_with_attached_checksum_db(main_db_path, checksum_db_path):
    import logging
    from fs_copy_tool.db import init_checksum_db
    import os
    # Ensure attached checksum DB has correct schema
    if not os.path.exists(checksum_db_path):
        init_checksum_db(checksum_db_path)
    else:
        # Try to create missing tables/indexes if DB exists but is incomplete
        try:
            init_checksum_db(checksum_db_path)
        except Exception as e:
            logging.error(f"Failed to ensure schema in attached checksum DB: {checksum_db_path}\nError: {e}")
            raise
    conn = RobustSqliteConn(main_db_path).connect()
    # Attach checksum DB as 'checksumdb'
    conn.execute(f"ATTACH DATABASE '{checksum_db_path}' AS checksumdb")
    return conn



def add_file_to_db(db_path, file_path):
    from pathlib import Path
    import sys
    from fs_copy_tool.utils.uidpath import UidPathUtil
    file = Path(file_path)
    if not file.is_file():
        logging.error(f"Error: {file_path} is not a file.")
        sys.exit(1)
    uid_path = UidPathUtil()
    uid_path_obj = uid_path.convert_path(str(file))
    uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
    if uid is None:
        logging.error(f"Error: Could not determine UID for {file_path}")
        sys.exit(1)
    try:
        stat = file.stat()
        with RobustSqliteConn(db_path).connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO source_files (uid, relative_path, size, last_modified)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(uid, relative_path) DO UPDATE SET
                    size=excluded.size,
                    last_modified=excluded.last_modified
            """, (uid, rel, stat.st_size, int(stat.st_mtime)))
            cur.execute("""
                INSERT INTO copy_status (uid, relative_path, status)
                VALUES (?, ?, 'pending')
                ON CONFLICT(uid, relative_path) DO UPDATE SET
                    status='pending'
            """, (uid, rel))
            conn.commit()
        logging.info(f"Added file: {file_path}")
    except Exception as e:
        logging.error(f"Error adding file: {file_path}\n{e}")
        sys.exit(1)

def add_source_to_db(db_path, src_dir):
    uid_path = UidPathUtil()
    src = Path(src_dir)
    if not src.is_dir():
        logging.error(f"Error: {src_dir} is not a directory.")
        return
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor
    files = [file for file in src.rglob("*") if file.is_file()]
    count = 0
    batch_size = max(100, len(files) // 10)  # 10 threads, each gets a batch
    from threading import Lock
    pbar_lock = Lock()
    def process_batch(batch):
        local_count = 0
        for file in batch:
            uid_path_obj = uid_path.convert_path(str(file))
            uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
            if uid is None:
                logging.error(f"Error: Could not determine UID for {file}")
                continue
            stat = file.stat()
            with RobustSqliteConn(db_path).connect() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO source_files (uid, relative_path, size, last_modified)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(uid, relative_path) DO UPDATE SET
                        size=excluded.size,
                        last_modified=excluded.last_modified
                """, (uid, rel, stat.st_size, int(stat.st_mtime)))
                cur.execute("""
                    INSERT INTO copy_status (uid, relative_path, status)
                    VALUES (?, ?, 'pending')
                    ON CONFLICT(uid, relative_path) DO UPDATE SET
                        status='pending'
                """, (uid, rel))
                conn.commit()
            local_count += 1
            with pbar_lock:
                pbar.update(1)
        return local_count
    batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]
    with tqdm(total=len(files), desc=f"Adding files from {src_dir}") as pbar:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(process_batch, batches)
            for batch_count in results:
                count += batch_count
    logging.info(f"Added {count} files from directory: {src_dir}")
    if count > 0:
        logging.info(f"Batch add complete: {count} files added from {src_dir}")

def list_files_in_db(db_path):
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM source_files ORDER BY uid, relative_path")
        rows = cur.fetchall()
        for row in rows:
            logging.info(f"{row[0]} | {row[1]} | size: {row[2]} | mtime: {row[3]}")
    logging.info(f"Total files: {len(rows)}")

def remove_file_from_db(db_path, file_path):
    file = Path(file_path)
    mount_id = str(file.parent)
    rel = file.name
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM source_files WHERE uid=? AND relative_path=?", (mount_id, rel))
        conn.commit()
    logging.info(f"Removed file: {file_path}")

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Non-Redundant Media File Copy Tool")
    subparsers = parser.add_subparsers(dest='command')
    # Add to destination index pool command (must be after subparsers is defined)
    parser_add_pool = subparsers.add_parser('add-to-destination-index-pool', help='Scan and add/update all files in the destination pool index')
    parser_add_pool.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_add_pool.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_add_pool.add_argument('--dst', required=True, help='Destination root directory to scan')

    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize a new job directory')
    parser_init.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_init.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Import checksums command (simplified, only from checksum_cache)
    parser_import = subparsers.add_parser('import-checksums', help='Import checksums from the checksum_cache table of another compatible database')
    parser_import.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_import.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_import.add_argument('--other-db', required=True, help='Path to other compatible SQLite database (must have checksum_cache table)')

    # Analyze, checksum, copy, etc. commands
    parser_analyze = subparsers.add_parser('analyze', help='Analyze source/destination volumes')
    parser_analyze.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_analyze.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_analyze.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_analyze.add_argument('--dst', nargs='+', help='Destination volume root(s)')

    parser_checksum = subparsers.add_parser('checksum', help='Update checksums for files')
    parser_checksum.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_checksum.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_checksum.add_argument('--table', choices=['source_files', 'destination_files'], required=True)
    parser_checksum.add_argument('--threads', type=int, default=4, help='Number of threads for checksum phase (default: 4)')
    parser_checksum.add_argument('--no-progress', action='store_true', help='Disable progress bar')

    parser_copy = subparsers.add_parser('copy', help='Copy files from source to destination. Skips already completed files and resumes incomplete jobs by default.')
    parser_copy.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_copy.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_copy.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_copy.add_argument('--dst', nargs='+', help='Destination volume root(s)')
    parser_copy.add_argument('--threads', type=int, default=4, help='Number of threads for copy phase (default: 4)')
    parser_copy.add_argument('--no-progress', action='store_true', help='Disable progress bar')
    parser_copy.add_argument('--resume', action='store_true', default=True, help='[Default] Resume incomplete jobs by skipping already completed files. This is always enabled.')

    # Resume command
    parser_resume = subparsers.add_parser('resume', help='Alias for copy: resumes incomplete or failed operations (skips completed files).')
    parser_resume.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_resume.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_resume.add_argument('--src', nargs='+', help='Source volume root(s)')
    parser_resume.add_argument('--dst', nargs='+', help='Destination volume root(s)')
    parser_resume.add_argument('--threads', type=int, default=4, help='Number of threads for copy phase (default: 4)')
    parser_resume.add_argument('--no-progress', action='store_true', help='Disable progress bar')

    # Status command
    parser_status = subparsers.add_parser('status', help='Show job progress and statistics')
    parser_status.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_status.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Log/Audit command
    parser_log = subparsers.add_parser('log', help='Show job log or audit trail')
    parser_log.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_log.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Shallow verify command (basic attributes)
    parser_shallow_verify = subparsers.add_parser('verify', help='Shallow or deep verify: check existence, size, last_modified, or checksums')
    parser_shallow_verify.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_shallow_verify.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_shallow_verify.add_argument('--stage', choices=['shallow', 'deep'], default='shallow', help='Verification stage: shallow (default) or deep')
    parser_shallow_verify.add_argument('--reverify', action='store_true', help='Force re-verification of all files, undoing any previous done status')

    # Deep verify command (checksums)
    parser_deep_verify = subparsers.add_parser('deep-verify', help='Deep verify: compare checksums between source and destination (always includes all shallow checks)')
    parser_deep_verify.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_deep_verify.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_deep_verify.add_argument('--reverify', action='store_true', help='Force re-verification of all files, undoing any previous done status')

    # Shallow verify status command
    parser_shallow_status = subparsers.add_parser('verify-status', help='Show a summary of the latest shallow verification results for each file')
    parser_shallow_status.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_shallow_status.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Deep verify status command
    parser_deep_status = subparsers.add_parser('deep-verify-status', help='Show a summary of the latest deep verification results for each file')
    parser_deep_status.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_deep_status.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Shallow verify status summary (short)
    parser_shallow_status_summary = subparsers.add_parser('verify-status-summary', help='Show a summary (short) of the latest shallow verification results for each file')
    parser_shallow_status_summary.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_shallow_status_summary.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Shallow verify status full (detailed)
    parser_shallow_status_full = subparsers.add_parser('verify-status-full', help='Show all shallow verification results (full history)')
    parser_shallow_status_full.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_shallow_status_full.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Deep verify status summary (short)
    parser_deep_status_summary = subparsers.add_parser('deep-verify-status-summary', help='Show a summary (short) of the latest deep verification results for each file')
    parser_deep_status_summary.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_deep_status_summary.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Deep verify status full (detailed)
    parser_deep_status_full = subparsers.add_parser('deep-verify-status-full', help='Show all deep verification results (full history)')
    parser_deep_status_full.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_deep_status_full.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Add file command
    parser_add_file = subparsers.add_parser('add-file', help='Add a single file to the job state/database')
    parser_add_file.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_add_file.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_add_file.add_argument('--file', required=True, help='Path to the file to add')

    # Add source command (recursive add)
    parser_add_source = subparsers.add_parser('add-source', help='Recursively add all files from a directory to the job state/database')
    parser_add_source.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_add_source.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_add_source.add_argument('--src', required=True, help='Source directory to add')

    # List files command
    parser_list_files = subparsers.add_parser('list-files', help='List all files currently in the job state/database')
    parser_list_files.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_list_files.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    # Remove file command
    parser_remove_file = subparsers.add_parser('remove-file', help='Remove a file from the job state/database')
    parser_remove_file.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_remove_file.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_remove_file.add_argument('--file', required=True, help='Path to the file to remove')

    # Summary phase command
    parser_summary = subparsers.add_parser('summary', help='Print summary and generate CSV report of errors and not-done files')
    parser_summary.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_summary.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    return parser.parse_args(args)

def main(args=None):
    parsed_args = parse_args(args)
    # Always set up logging with job_dir if available
    job_dir = getattr(parsed_args, 'job_dir', None)
    from fs_copy_tool.utils.logging_config import setup_logging
    setup_logging(job_dir)
    return run_main_command(parsed_args)


def handle_summary(args):
    from fs_copy_tool.phases.summary import summary_phase
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    summary_phase(db_path, args.job_dir)
    return 0

def handle_init(args):
    init_job_dir(args.job_dir, args.job_name, getattr(args, 'checksum_db', None))
    return 0

def handle_analyze(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    init_db(db_path)
    if args.src:
        analyze_volumes(db_path, args.src, 'source_files')
    if args.dst:
        analyze_volumes(db_path, args.dst, 'destination_files')
    return 0

def handle_copy(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
    init_db(db_path)
    from fs_copy_tool.utils.checksum_cache import ChecksumCache
    from tqdm import tqdm
    import sqlite3
    def conn_factory():
        return RobustSqliteConn(db_path).connect()
    checksum_cache = ChecksumCache(conn_factory, UidPathUtil())
    # Get all files in the destination pool
    with conn_factory() as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path FROM destination_pool_files")
        pool_files = cur.fetchall()
    if pool_files:
        from concurrent.futures import ThreadPoolExecutor
        from threading import Lock
        pbar_lock = Lock()
        uid_path = UidPathUtil()
        def process_pool_file(args):
            uid, rel_path = args
            uid_path_obj = UidPath(uid, rel_path)
            abs_path = uid_path.reconstruct_path(uid_path_obj)
            if abs_path is None:
                logging.warning(f"[COPY][POOL] Skipping file: could not reconstruct path for uid={uid}, rel_path={rel_path}")
                return
            checksum_cache.get_or_compute_with_invalidation(abs_path)
            with pbar_lock:
                pbar.update(1)
        with tqdm(total=len(pool_files), desc="Updating pool checksums") as pbar:
            with ThreadPoolExecutor() as executor:
                list(executor.map(process_pool_file, pool_files))
    # Step 2: Always check both path and pool deduplication in copy_files
    copy_files(db_path, args.src, args.dst, threads=args.threads)
    return 0

def handle_verify(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    # Remove src and dst, just use db_path and stage
    if args.stage == 'shallow':
        shallow_verify_files(db_path, reverify=getattr(args, 'reverify', False))
        with RobustSqliteConn(db_path).connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT verify_status, COUNT(*) FROM verification_shallow_results
                GROUP BY verify_status
            ''')
            print("\n================ SHALLOW VERIFICATION SUMMARY ================")
            results = cur.fetchall()
            if results:
                for status, count in results:
                    print(f"  {status}: {count}")
            else:
                print("  No files verified.")
            print("============================================================\n")
    else:
        deep_verify_files(db_path, reverify=getattr(args, 'reverify', False))
        error_count = 0
        with RobustSqliteConn(db_path).connect() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT verify_status, COUNT(*) FROM verification_deep_results
                GROUP BY verify_status
            ''')
            print("\n================= DEEP VERIFICATION SUMMARY =================")
            status_counts = {status: count for status, count in cur.fetchall()}
            if status_counts:
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
            else:
                print("  No files verified.")
            print("============================================================\n")
            error_count = status_counts.get('error', 0) + status_counts.get('failed', 0)
            if error_count:
                print("\nErrors:")
                cur.execute('''
                    SELECT relative_path, verify_error FROM verification_deep_results
                    WHERE verify_status IN ('error', 'failed')
                    ORDER BY relative_path
                ''')
                for row in cur.fetchall():
                    print(f"{row[0]} | error: {row[1]}")
        if error_count:
            return 1
    return 0

def handle_resume(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    init_db(db_path)
    copy_files(db_path, args.src, args.dst)
    return 0

def handle_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM copy_status WHERE status='done'")
        done = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM copy_status WHERE status='pending' OR status IS NULL")
        pending = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM copy_status WHERE status='error'")
        error = cur.fetchone()[0]
        print("\n====================== JOB STATUS SUMMARY ======================")
        print(f"  Done:    {done}")
        print(f"  Pending: {pending}")
        print(f"  Error:   {error}")
        print("==============================================================\n")
    return 0

def handle_log(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        logging.info('Copied files (destination_files):')
        cur.execute("""
            SELECT d.uid, d.relative_path, d.size, d.last_modified, s.status
            FROM destination_files d
            JOIN copy_status s ON d.uid = s.uid AND d.relative_path = s.relative_path
            WHERE s.status='done'
        """)
        for row in cur.fetchall():
            logging.info(f"{row[0]} | {row[1]} | size: {row[2]} | mtime: {row[3]} | status: {row[4]}")
        logging.info('---')
        logging.info('Errors (source_files):')
        cur.execute("""
            SELECT s.uid, s.relative_path, s.status, s.error_message
            FROM copy_status s
            WHERE s.status='error'
        """)
        for row in cur.fetchall():
            logging.warning(f"{row[0]} | {row[1]} | status: {row[2]} | error: {row[3]}")
    return 0

def handle_deep_verify(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    deep_verify_files(db_path, reverify=getattr(args, 'reverify', False))
    return 0

def handle_verify_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        logging.info('Shallow Verification Results:')
        cur.execute('''
            SELECT relative_path, verify_status, verify_error, expected_size, actual_size, expected_last_modified, actual_last_modified
            FROM verification_shallow_results
            WHERE timestamp = (SELECT MAX(timestamp) FROM verification_shallow_results vs2 WHERE vs2.relative_path = verification_shallow_results.relative_path)
            ORDER BY relative_path
        ''')
        for row in cur.fetchall():
            logging.info(f"{row[0]} | status: {row[1]} | error: {row[2]} | size: {row[4]}/{row[3]} | mtime: {row[6]}/{row[5]}")
    return 0

def handle_deep_verify_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        logging.info('Deep Verification Results:')
        cur.execute('''
            SELECT relative_path, verify_status, verify_error, expected_checksum, src_checksum, dst_checksum, timestamp
            FROM verification_deep_results
            WHERE timestamp = (SELECT MAX(timestamp) FROM verification_deep_results vd2 WHERE vd2.relative_path = verification_deep_results.relative_path)
            ORDER BY relative_path
        ''')
        for row in cur.fetchall():
            logging.info(f"{row[0]} | status: {row[1]} | error: {row[2]} | expected: {row[3]} | src: {row[4]} | dst: {row[5]} | ts: {row[6]}")
    return 0

def handle_add_file(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    add_file_to_db(db_path, args.file)
    return 0

def handle_add_source(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    add_source_to_db(db_path, args.src)
    return 0

def handle_list_files(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    list_files_in_db(db_path)
    return 0

def handle_remove_file(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    remove_file_from_db(db_path, args.file)
    return 0

def handle_checksum(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
    init_db(db_path)
    uid_path = UidPathUtil()
    def conn_factory():
        return RobustSqliteConn(checksum_db_path).connect()
    checksum_cache = ChecksumCache(conn_factory, uid_path)
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT uid, relative_path, size, last_modified FROM {args.table}")
        rows = cur.fetchall()
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import logging
    def process_row(row):
        uid, rel_path, size, last_modified = row
        uid_path_obj = UidPath(uid, rel_path)
        file_path = uid_path.reconstruct_path(uid_path_obj)
        logging.info(f"[handle_checksum] Processing: uid={uid}, rel_path={rel_path}, resolved_path={file_path}")
        if not file_path or not file_path.exists():
            logging.info(f"[handle_checksum] File not found or does not exist: {file_path}")
            return None
        logging.info(f"[handle_checksum] Calling get_or_compute_with_invalidation for {file_path}")
        checksum = checksum_cache.get_or_compute_with_invalidation(str(file_path))
        logging.info(f"[handle_checksum] Checksum for {file_path}: {checksum}")
        return True if checksum else None
    with tqdm(total=len(rows), desc=f"Checksumming {args.table}") as pbar:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(process_row, row) for row in rows]
            for f in as_completed(futures):
                pbar.update(1)
    return 0

def handle_import_checksums(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
    other_db_path = args.other_db
    # Validate schema of other_db
    with RobustSqliteConn(other_db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checksum_cache'")
        if not cur.fetchone():
            logging.error(f"Error: The other database does not have a checksum_cache table.")
            sys.exit(1)
        # Import all rows from other checksum_cache
        cur.execute("SELECT uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid FROM checksum_cache")
        rows = cur.fetchall()
    # Insert into attached checksum DB
    logging.info(f"Rows to import from other DB: {len(rows)} rows")
    from tqdm import tqdm
    conn = connect_with_attached_checksum_db(db_path, checksum_db_path)
    try:
        cur = conn.cursor()
        with tqdm(total=len(rows), desc="Importing checksums", unit="row") as pbar:
            for row in rows:
                cur.execute("""
                    INSERT OR REPLACE INTO checksumdb.checksum_cache (uid, relative_path, size, last_modified, checksum, imported_at, last_validated, is_valid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, row)
                pbar.update(1)
        conn.commit()
        # Log all rows in checksum_cache after import
        cur.execute("SELECT COUNT(*) FROM checksumdb.checksum_cache")
        count = cur.fetchone()[0]
        logging.info(f"All rows in main job's checksum_cache after import: {count} rows")
    finally:
        conn.close()
    logging.info(f"Imported {len(rows)} checksums from {other_db_path} into checksum_cache.")
    return 0

def run_main_command(args):
    if getattr(args, 'command', None) == 'add-to-destination-index-pool':
        return handle_add_to_destination_index_pool(args)
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
    elif args.command == 'summary':
        return handle_summary(args)

    logging.error("No command specified or unknown command.")
    return 1

if __name__ == "__main__":
    setup_logging()
    main()
