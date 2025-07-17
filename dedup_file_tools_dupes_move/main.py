
import argparse
import logging
import os
from dedup_file_tools_commons.utils.logging_config import setup_logging
from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir
from dedup_file_tools_fs_copy.db import init_db
from dedup_file_tools_dupes_move.phases.analysis import find_and_queue_duplicates
from dedup_file_tools_dupes_move.phases.move import move_duplicates

def init_job_dir(job_dir, job_name, checksum_db=None):
    from dedup_file_tools_fs_copy.db import init_db, init_checksum_db
    os.makedirs(job_dir, exist_ok=True)
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    checksum_db_path = checksum_db or os.path.join(job_dir, 'checksum-cache.db')
    init_db(db_path)
    if not os.path.exists(checksum_db_path):
        init_checksum_db(checksum_db_path)
    logging.info(f"Initialized job directory at {job_dir} with database {db_path} and checksum DB {checksum_db_path}")

    parser = argparse.ArgumentParser(description="Move duplicate files by checksum, preserving one copy per group.")
    parser.add_argument('-c', '--config', help='Path to YAML configuration file', default=None)
    parser.add_argument('--log-level', default='WARNING', help='Set logging level (default: WARNING)')
    subparsers = parser.add_subparsers(dest='command')

    parser_init = subparsers.add_parser('init', help='Initialize a new job directory')
    parser_init.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_init.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    parser_analyze = subparsers.add_parser('analyze', help='Scan for duplicates and queue for move')
    parser_analyze.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_analyze.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_analyze.add_argument('--src', required=True, help='Source directory to scan')
    parser_analyze.add_argument('--threads', type=int, default=4, help='Number of threads')

    parser_move = subparsers.add_parser('move', help='Move queued duplicates to destination')
    parser_move.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_move.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')
    parser_move.add_argument('--dest', required=True, help='Destination root for moved files')
    parser_move.add_argument('--threads', type=int, default=4, help='Number of threads')
    parser_move.add_argument('--dry-run', action='store_true', help='Dry run (do not actually move files)')

    parser_status = subparsers.add_parser('status', help='Show job progress and statistics')
    parser_status.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_status.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    parser_summary = subparsers.add_parser('summary', help='Print summary and generate CSV report of errors and not-done files')
    parser_summary.add_argument('--job-dir', required=True, help='Path to job directory')
    parser_summary.add_argument('--job-name', required=True, help='Name of the job (database file will be <job-name>.db)')

    parsed_args = parser.parse_args(args)
    # If config is provided, load YAML and merge
    if getattr(parsed_args, 'config', None):
        from dedup_file_tools_dupes_move.utils.config_loader import load_yaml_config, merge_config_with_args
        config_dict = load_yaml_config(parsed_args.config)
        parsed_args = merge_config_with_args(parsed_args, config_dict, parser)
    return parsed_args

def handle_init(args):
    init_job_dir(args.job_dir, args.job_name)
    return 0

def handle_analyze(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    init_db(db_path)
    find_and_queue_duplicates(db_path, args.src, threads=args.threads)
    return 0

def handle_move(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    move_duplicates(db_path, args.dest, threads=args.threads, dry_run=args.dry_run)
    return 0

def handle_status(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM move_status WHERE status='done'")
        done = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM move_status WHERE status='pending' OR status IS NULL")
        pending = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM move_status WHERE status='error'")
        error = cur.fetchone()[0]
        print("\n====================== JOB STATUS SUMMARY ======================")
        print(f"  Done:    {done}")
        print(f"  Pending: {pending}")
        print(f"  Error:   {error}")
        print("==============================================================\n")
    return 0

def handle_summary(args):
    db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
    print("\n==== SUMMARY PHASE ====")
    print(f"Job directory: {args.job_dir}")
    from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
    conn = RobustSqliteConn(db_path).connect()
    cur = conn.cursor()
    cur.execute("""
        SELECT uid, relative_path, status, error_message
        FROM move_status
        WHERE status != 'done'
    """)
    rows = cur.fetchall()
    if not rows:
        print("All files moved successfully. No errors or pending files.")
    else:
        print(f"{len(rows)} files not moved successfully. See below:")
        for row in rows:
            print(f"{row[0]} | {row[1]} | status: {row[2]} | error: {row[3]}")
    conn.close()
    return 0

def main(args=None):
    parsed_args = parse_args(args)
    setup_logging(parsed_args.job_dir if hasattr(parsed_args, 'job_dir') else None, log_level=getattr(parsed_args, 'log_level', None))
    if getattr(parsed_args, 'command', None) == 'init':
        return handle_init(parsed_args)
    elif parsed_args.command == 'analyze':
        return handle_analyze(parsed_args)
    elif parsed_args.command == 'move':
        return handle_move(parsed_args)
    elif parsed_args.command == 'status':
        return handle_status(parsed_args)
    elif parsed_args.command == 'summary':
        return handle_summary(parsed_args)
    else:
        print("No command specified or unknown command.")
        return 1

if __name__ == "__main__":
    main()
