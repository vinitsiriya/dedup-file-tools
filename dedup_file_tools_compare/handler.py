
import os
import sqlite3
from dedup_file_tools_compare.db import init_db
from dedup_file_tools_compare.phases.add_to_pool import add_directory_to_pool

def handle_add_to_pool(args, side):
    from dedup_file_tools_compare.paths import get_db_path, setup_logging_for_job
    db_path = get_db_path(args.job_dir, args.job_name)
    table = 'left_pool_files' if side == 'left' else 'right_pool_files'
    directory = args.dir
    if not os.path.exists(db_path):
        init_db(db_path)
    setup_logging_for_job(args.job_dir)
    import logging
    logging.info(f"Adding files from {directory} to {side} pool in {db_path}")
    add_directory_to_pool(db_path, directory, table)
    logging.info(f"Added files from {directory} to {side} pool in {db_path}")
    # Ensure checksum cache is up to date for this pool
    from dedup_file_tools_compare.phases.ensure_pool_checksums import ensure_pool_checksums
    ensure_pool_checksums(args.job_dir, args.job_name, table)
    logging.info(f"Checksums ensured for {side} pool.")

def handle_find_missing_files(args):
    from dedup_file_tools_compare.phases.compare import find_missing_files
    from dedup_file_tools_compare.paths import get_db_path, setup_logging_for_job
    db_path = get_db_path(args.job_dir, args.job_name)
    setup_logging_for_job(args.job_dir)
    import logging
    logging.info(f"Running find_missing_files for job_dir={args.job_dir}, job_name={args.job_name}")
    find_missing_files(db_path, threads=args.threads, no_progress=args.no_progress, left=args.left, right=args.right, both=args.both)

def handle_show_result(args):
    from dedup_file_tools_compare.phases.results import show_result
    from dedup_file_tools_compare.paths import get_db_path, get_csv_path, setup_logging_for_job
    db_path = get_db_path(args.job_dir, args.job_name)
    setup_logging_for_job(args.job_dir)
    import logging
    logging.info(f"Showing result for job_dir={args.job_dir}, job_name={args.job_name}")
    # If output is not specified, use default CSV path
    output = args.output or get_csv_path(args.job_dir)
    show_result(db_path, summary=args.summary, full_report=args.full_report, output=output, show=args.show)
    logging.info(f"Results written to {output}")
