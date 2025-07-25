from dedup_file_tools_commons.utils.logging_config import setup_logging
"""
File: dedup_file_tools_fs_copy/main.py
Main Orchestration & CLI Entry Point

Description:
    This is the main orchestration module and CLI entry point for the Non-Redundant Media File Copy Tool. It parses command-line arguments, initializes job directories and databases, and coordinates the execution of all workflow phases: analysis, checksum, copy, verify, and summary. It provides a robust, resumable, and auditable workflow for deduplicated file copying, supporting both one-shot and stepwise operation modes.

Key Features:
    - CLI interface with subcommands for each workflow phase and utility
    - One-shot mode for full end-to-end operation
    - Modular handlers for each phase (init, analyze, checksum, copy, verify, summary, etc.)
    - Database and checksum cache management
    - Logging and progress reporting
    - Designed for both interactive and automated/agent-driven use

Usage:
    Run as a standalone script or module to perform deduplicated file copy operations. Supports both full workflow and individual phase execution via CLI subcommands.
"""
from dedup_file_tools_commons.db import init_checksum_db


def handle_add_to_destination_index_pool(args):
    from dedup_file_tools_fs_copy.utils.destination_pool_cli import add_to_destination_index_pool
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    add_to_destination_index_pool(db_path, args.dst)
    return 0


import argparse
import logging
import sys
import os
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from pathlib import Path
from dedup_file_tools_fs_copy.db import init_db
from dedup_file_tools_fs_copy.phases.analysis import analyze_directories
from dedup_file_tools_fs_copy.phases.copy import copy_files
from dedup_file_tools_fs_copy.phases.verify import shallow_verify_files, deep_verify_files
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
## removed duplicate import of setup_logging

def init_job_dir(job_dir, job_name, checksum_db=None):
    from dedup_file_tools_fs_copy.db import init_db
    from dedup_file_tools_commons.db import init_checksum_db
    os.makedirs(job_dir, exist_ok=True)
    db_path = os.path.join(job_dir, f'{job_name}.db')
    checksum_db_path = checksum_db or os.path.join(job_dir, 'checksum-cache.db')
    init_db(db_path)
    if not os.path.exists(checksum_db_path):
        init_checksum_db(checksum_db_path)
    logging.info(f"[AGENT][MAIN] Initialized job directory at {job_dir} with database {db_path} and checksum DB {checksum_db_path}")


# Path utilities from commons
from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir, get_checksum_db_path

# Centralized DB connection with attached checksum DB
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db



def add_file_to_db(db_path, file_path):
    from pathlib import Path
    import sys
    from dedup_file_tools_commons.utils.uidpath import UidPathUtil
    file = Path(file_path)
    if not file.is_file():
        logging.error(f"[AGENT][MAIN] Error: {file_path} is not a file.")
        sys.exit(1)
    uid_path = UidPathUtil()
    uid_path_obj = uid_path.convert_path(str(file))
    uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
    if uid is None:
        logging.error(f"[AGENT][MAIN] Error: Could not determine UID for {file_path}")
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
        logging.info(f"[AGENT][MAIN] Added file: {file_path}")
    except Exception as e:
        logging.error(f"[AGENT][MAIN] Error adding file: {file_path}\n{e}")
        sys.exit(1)

def add_source_to_db(db_path, src_dir):
    uid_path = UidPathUtil()
    src = Path(src_dir)
    if not src.is_dir():
        logging.error(f"[AGENT][MAIN] Error: {src_dir} is not a directory.")
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
    logging.info(f"[AGENT][MAIN] Added {count} files from directory: {src_dir}")
    if count > 0:
        logging.info(f"[AGENT][MAIN] Batch add complete: {count} files added from {src_dir}")

def list_files_in_db(db_path):
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, size, last_modified FROM source_files ORDER BY uid, relative_path")
        rows = cur.fetchall()
        for row in rows:
            logging.info(f"[AGENT][MAIN] {row[0]} | {row[1]} | size: {row[2]} | mtime: {row[3]}")
    logging.info(f"[AGENT][MAIN] Total files: {len(rows)}")

def remove_file_from_db(db_path, file_path):
    file = Path(file_path)
    mount_id = str(file.parent)
    rel = file.name
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM source_files WHERE uid=? AND relative_path=?", (mount_id, rel))
        conn.commit()
    logging.info(f"[AGENT][MAIN] Removed file: {file_path}")

def parse_args(args=None):
    parser = argparse.ArgumentParser(description="Non-Redundant Media File Copy Tool")
    parser.add_argument('-c', '--config', help='Path to YAML configuration file', default=None)
    subparsers = parser.add_subparsers(dest='command')
    # Interactive config generator command
    parser_generate_config = subparsers.add_parser('generate-config', help='Interactively generate a YAML config file for use with -c')

    # One-shot command (must be after subparsers is defined)
    parser_one_shot = subparsers.add_parser('one-shot', help='Run the full workflow (init, import, add-source, add-to-destination-index-pool, analyze, checksum, copy, verify, summary) in one command')
    parser_one_shot.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_one_shot.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_one_shot.add_argument('--src', nargs='+', required=True, help='Source volume root(s)')
    parser_one_shot.add_argument('--dst', nargs='+', required=True, help='Destination volume root(s)')
    parser_one_shot.add_argument('--log-level', default='WARNING', help='Set logging level (default: WARNING)')
    parser_one_shot.add_argument('--threads', type=int, default=4, help='Number of threads for parallel operations (default: 4)')
    parser_one_shot.add_argument('--no-progress', action='store_true', help='Disable progress bars')
    parser_one_shot.add_argument('--resume', action='store_true', default=True, help='Resume incomplete jobs (default: True for copy phase)')
    parser_one_shot.add_argument('--reverify', action='store_true', help='Force re-verification in verify/deep-verify')
    parser_one_shot.add_argument('--checksum-db', help='Custom checksum DB path (default: <job-dir>/checksum-cache.db)')
    parser_one_shot.add_argument('--other-db', help='Path to another compatible SQLite database for importing checksums')
    parser_one_shot.add_argument('--table', choices=['source_files', 'destination_files'], default='source_files', help='Table to use for checksumming (default: source_files)')
    parser_one_shot.add_argument('--stage', choices=['shallow', 'deep'], default='shallow', help='Verification stage (default: shallow)')
    parser_one_shot.add_argument('--skip-verify', action='store_true', help='Skip verification steps')
    parser_one_shot.add_argument('--deep-verify', action='store_true', help='Perform deep verification after shallow verification')
    parser_one_shot.add_argument('--dst-index-pool', help='Path to destination index pool (default: value of --dst)')
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

    # Parse args first
    parsed_args = parser.parse_args(args)
    # If config is provided, load YAML and merge
    if getattr(parsed_args, 'config', None):
        from dedup_file_tools_fs_copy.utils.config_loader import load_yaml_config, merge_config_with_args
        config_dict = load_yaml_config(parsed_args.config)
        parsed_args = merge_config_with_args(parsed_args, config_dict, parser)
    return parsed_args

def main(args=None):
    parsed_args = parse_args(args)
    # Set up logging only once, prefer file logging if job_dir is available
    job_dir = getattr(parsed_args, 'job_dir', None)
    log_level = getattr(parsed_args, 'log_level', None)
    setup_logging(log_level=log_level, job_dir=job_dir)
    logging.info(f"[AGENT][MAIN] main() called with args: {args}")
    if getattr(parsed_args, 'command', None) == 'generate-config':
        logging.info("[AGENT][MAIN] Entering interactive config generator phase.")
        from dedup_file_tools_fs_copy.utils.interactive_config import interactive_config_generator
        interactive_config_generator()
        logging.info("[AGENT][MAIN] Interactive config generator phase complete.")
        return 0
    logging.info(f"[AGENT][MAIN] Entering main command phase: {getattr(parsed_args, 'command', None)}")
    result = run_main_command(parsed_args)
    logging.info(f"[AGENT][MAIN] Main command phase complete with result: {result}")
    return result


def handle_summary(args):
    from dedup_file_tools_fs_copy.phases.summary import summary_phase
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
        analyze_directories(db_path, args.src, 'source_files')
    if args.dst:
        analyze_directories(db_path, args.dst, 'destination_files')
    return 0

def handle_copy(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
    init_db(db_path)
    # Ensure destination pool checksums before copy
    from dedup_file_tools_fs_copy.phases.ensure_destination_pool import ensure_destination_pool_checksums
    ensure_destination_pool_checksums(
        job_dir=args.job_dir,
        job_name=args.job_name,
        checksum_db=checksum_db_path
    )
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
        logging.info('[AGENT][MAIN] Copied files (destination_files):')
        cur.execute("""
            SELECT d.uid, d.relative_path, d.size, d.last_modified, s.status
            FROM destination_files d
            JOIN copy_status s ON d.uid = s.uid AND d.relative_path = s.relative_path
            WHERE s.status='done'
        """)
        for row in cur.fetchall():
            logging.info(f"[AGENT][MAIN] {row[0]} | {row[1]} | size: {row[2]} | mtime: {row[3]} | status: {row[4]}")
        logging.info('[AGENT][MAIN] ---')
        logging.info('[AGENT][MAIN] Errors (source_files):')
        cur.execute("""
            SELECT s.uid, s.relative_path, s.status, s.error_message
            FROM copy_status s
            WHERE s.status='error'
        """)
        for row in cur.fetchall():
            logging.warning(f"[AGENT][MAIN] {row[0]} | {row[1]} | status: {row[2]} | error: {row[3]}")
    return 0

def handle_deep_verify(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    deep_verify_files(db_path, reverify=getattr(args, 'reverify', False))
    return 0

def handle_verify_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        logging.info('[AGENT][MAIN] Shallow Verification Results:')
        cur.execute('''
            SELECT relative_path, verify_status, verify_error, expected_size, actual_size, expected_last_modified, actual_last_modified
            FROM verification_shallow_results
            WHERE timestamp = (SELECT MAX(timestamp) FROM verification_shallow_results vs2 WHERE vs2.relative_path = verification_shallow_results.relative_path)
            ORDER BY relative_path
        ''')
        for row in cur.fetchall():
            logging.info(f"[AGENT][MAIN] {row[0]} | status: {row[1]} | error: {row[2]} | size: {row[4]}/{row[3]} | mtime: {row[6]}/{row[5]}")
    return 0

def handle_deep_verify_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        logging.info('[AGENT][MAIN] Deep Verification Results:')
        cur.execute('''
            SELECT relative_path, verify_status, verify_error, expected_checksum, src_checksum, dst_checksum, timestamp
            FROM verification_deep_results
            WHERE timestamp = (SELECT MAX(timestamp) FROM verification_deep_results vd2 WHERE vd2.relative_path = verification_deep_results.relative_path)
            ORDER BY relative_path
        ''')
        for row in cur.fetchall():
            logging.info(f"[AGENT][MAIN] {row[0]} | status: {row[1]} | error: {row[2]} | expected: {row[3]} | src: {row[4]} | dst: {row[5]} | ts: {row[6]}")
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
    from dedup_file_tools_fs_copy.phases.checksum import run_checksum_table
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
    init_db(db_path)
    return run_checksum_table(
        db_path=db_path,
        checksum_db_path=checksum_db_path,
        table=args.table,
        threads=getattr(args, 'threads', 4),
        no_progress=getattr(args, 'no_progress', False)
    )

def handle_import_checksums(args):
    from dedup_file_tools_fs_copy.phases.import_checksum import run_import_checksums
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
    other_db_path = args.other_db
    return run_import_checksums(db_path, checksum_db_path, other_db_path)

def run_main_command(args):
    if getattr(args, 'command', None) == 'one-shot':
        # Step 1: Init job dir
        try:
            init_job_dir(args.job_dir, args.job_name, getattr(args, 'checksum_db', None))
        except Exception as e:
            print(f"Error in init_job_dir: {e}")
            return 1
        # Step 2: Import checksums if provided
        if getattr(args, 'other_db', None):
            class ImportArgs: pass
            import_args = ImportArgs()
            import_args.job_dir = args.job_dir
            import_args.job_name = args.job_name
            import_args.other_db = args.other_db
            import_args.checksum_db = getattr(args, 'checksum_db', None)
            rc = handle_import_checksums(import_args)
            if rc != 0:
                print("Error in import-checksums step.")
                return rc
        # Step 3: Add source
        class AddSourceArgs: pass
        add_source_args = AddSourceArgs()
        add_source_args.job_dir = args.job_dir
        add_source_args.job_name = args.job_name
        add_source_args.src = args.src[0] if isinstance(args.src, list) else args.src
        rc = handle_add_source(add_source_args)
        if rc is not None and rc != 0:
            print("Error in add-source step.")
            return rc
        # Step 4: Add to destination index pool and ensure destination pool checksums
        dst_index_pool = getattr(args, 'dst_index_pool', None) or (args.dst[0] if isinstance(args.dst, list) else args.dst)
        class AddPoolArgs: pass
        add_pool_args = AddPoolArgs()
        add_pool_args.job_dir = args.job_dir
        add_pool_args.job_name = args.job_name
        add_pool_args.dst = dst_index_pool
        rc = handle_add_to_destination_index_pool(add_pool_args)
        if rc is not None and rc != 0:
            print("Error in add-to-destination-index-pool step.")
            return rc
        # Ensure destination pool checksums using the new explicit function
        from dedup_file_tools_fs_copy.phases.ensure_destination_pool import ensure_destination_pool_checksums
        db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
        checksum_db_path = get_checksum_db_path(args.job_dir, getattr(args, 'checksum_db', None))
        ensure_destination_pool_checksums(
            job_dir=args.job_dir,
            job_name=args.job_name,
            checksum_db=checksum_db_path
        )
        # Step 5: Analyze
        class AnalyzeArgs: pass
        analyze_args = AnalyzeArgs()
        analyze_args.job_dir = args.job_dir
        analyze_args.job_name = args.job_name
        analyze_args.src = args.src
        analyze_args.dst = args.dst
        rc = handle_analyze(analyze_args)
        if rc is not None and rc != 0:
            print("Error in analyze step.")
            return rc
        # Step 6: Checksums (source)
        class ChecksumArgs: pass
        checksum_args = ChecksumArgs()
        checksum_args.job_dir = args.job_dir
        checksum_args.job_name = args.job_name
        checksum_args.table = 'source_files'
        checksum_args.threads = args.threads
        checksum_args.no_progress = args.no_progress
        checksum_args.checksum_db = getattr(args, 'checksum_db', None)
        rc = handle_checksum(checksum_args)
        if rc is not None and rc != 0:
            print("Error in checksum (source_files) step.")
            return rc
        # Step 7: Checksums (destination)
        checksum_args.table = 'destination_files'
        rc = handle_checksum(checksum_args)
        if rc is not None and rc != 0:
            print("Error in checksum (destination_files) step.")
            return rc
        # Step 8: Copy
        class CopyArgs: pass
        copy_args = CopyArgs()
        copy_args.job_dir = args.job_dir
        copy_args.job_name = args.job_name
        copy_args.src = args.src
        copy_args.dst = args.dst
        copy_args.threads = args.threads
        copy_args.no_progress = args.no_progress
        copy_args.resume = args.resume
        rc = handle_copy(copy_args)
        if rc is not None and rc != 0:
            print("Error in copy step.")
            return rc
        # Step 9: Verify (shallow)
        if not args.skip_verify:
            class VerifyArgs: pass
            verify_args = VerifyArgs()
            verify_args.job_dir = args.job_dir
            verify_args.job_name = args.job_name
            verify_args.stage = 'shallow'
            verify_args.reverify = args.reverify
            rc = handle_verify(verify_args)
            if rc is not None and rc != 0:
                print("Error in verify (shallow) step.")
                return rc
            # Step 10: Verify (deep) if requested
            if args.deep_verify or args.stage == 'deep':
                verify_args.stage = 'deep'
                rc = handle_verify(verify_args)
                if rc is not None and rc != 0:
                    print("Error in verify (deep) step.")
                    return rc
        # Step 11: Summary
        class SummaryArgs: pass
        summary_args = SummaryArgs()
        summary_args.job_dir = args.job_dir
        summary_args.job_name = args.job_name
        rc = handle_summary(summary_args)
        if rc is not None and rc != 0:
            print("Error in summary step.")
            return rc
        print("Done")
        return 0
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

    logging.error("[AGENT][MAIN] No command specified or unknown command.")
    return 1

if __name__ == "__main__":
    logging.info("[AGENT][MAIN] Program started.")
    try:
        main()
        logging.info("[AGENT][MAIN] Program finished successfully.")
    except Exception as e:
        logging.exception(f"[AGENT][MAIN] Unhandled exception: {e}")
        raise
