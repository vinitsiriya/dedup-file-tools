
import argparse
import sys
import os
import logging
from dedup_file_tools_compare.db import init_db
from dedup_file_tools_commons.utils.logging_config import setup_logging


def parse_args(argv=None):
    parser = argparse.ArgumentParser(prog='dedup-file-compare')
    parser.add_argument('--config', type=str, help='YAML config file')
    parser.add_argument('--log-level', type=str, default='WARNING', help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--log-file', type=str, help='Custom log file path (default: job logs dir)')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # one-shot
    p_oneshot = subparsers.add_parser('one-shot', help='Run the full workflow (init, add-to-left, add-to-right, find-missing-files, show-result) in one command (always compares by checksum)')
    p_oneshot.add_argument('--job-dir', required=True)
    p_oneshot.add_argument('--job-name', required=True)
    p_oneshot.add_argument('--left', required=True, help='Left directory to compare')
    p_oneshot.add_argument('--right', required=True, help='Right directory to compare')
    p_oneshot.add_argument('--threads', type=int, default=4)
    p_oneshot.add_argument('--no-progress', action='store_true')
    p_oneshot.add_argument('--output', type=str, help='Output file for results (CSV or JSON)')
    p_oneshot.add_argument('--show', choices=['identical', 'different', 'unique-left', 'unique-right', 'all'], default='all')
    p_oneshot.add_argument('--summary', action='store_true', help='Show summary (default)')
    p_oneshot.add_argument('--full-report', action='store_true', help='Show full report')
    p_oneshot.add_argument('--use-normal-paths', action='store_true', help='Output absolute paths in the report (adds absolute_path column)')
    # import-checksums
    p_import = subparsers.add_parser('import-checksums', help='Import checksums from the checksum_cache table of another compatible database')
    p_import.add_argument('--job-dir', required=True)
    p_import.add_argument('--job-name', required=True)
    p_import.add_argument('--other-db', required=True, help='Path to other compatible SQLite database (must have checksum_cache table)')

    # init
    p_init = subparsers.add_parser('init', help='Initialize a new comparison job')
    p_init.add_argument('--job-dir', required=True)
    p_init.add_argument('--job-name', required=True)

    # add-to-left
    p_left = subparsers.add_parser('add-to-left', help='Add files from a directory to the left pool')
    p_left.add_argument('--job-dir', required=True)
    p_left.add_argument('--job-name', required=True)
    p_left.add_argument('--dir', required=True)

    # add-to-right
    p_right = subparsers.add_parser('add-to-right', help='Add files from a directory to the right pool')
    p_right.add_argument('--job-dir', required=True)
    p_right.add_argument('--job-name', required=True)
    p_right.add_argument('--dir', required=True)

    # find-missing-files
    p_find = subparsers.add_parser('find-missing-files', help='Find files missing from one or both sides (always compares by checksum)')
    p_find.add_argument('--job-dir', required=True)
    p_find.add_argument('--job-name', required=True)
    p_find.add_argument('--threads', type=int, default=4)
    p_find.add_argument('--no-progress', action='store_true')
    p_find.add_argument('--left', action='store_true')
    p_find.add_argument('--right', action='store_true')
    p_find.add_argument('--both', action='store_true')

    # show-result
    p_show = subparsers.add_parser('show-result', help='Show or export the comparison results')
    p_show.add_argument('--job-dir', required=True)
    p_show.add_argument('--job-name', required=True)
    p_show.add_argument('--summary', action='store_true')
    p_show.add_argument('--full-report', action='store_true')
    p_show.add_argument('--output', type=str)
    p_show.add_argument('--show', choices=['identical', 'different', 'unique-left', 'unique-right', 'all'], default='all')
    p_show.add_argument('--use-normal-paths', action='store_true', help='Output absolute paths in the report (adds absolute_path column)')

    return parser.parse_args(argv)

def run_main_command(args):
    if args.command == 'one-shot':
        # Logging is already set up in main()
        # 1. init
        db_path = os.path.join(args.job_dir, f"{args.job_name}.db")
        if not os.path.exists(args.job_dir):
            os.makedirs(args.job_dir)
        if not os.path.exists(db_path):
            init_db(db_path)
        # 2. add-to-left
        from types import SimpleNamespace
        from dedup_file_tools_compare.handler import handle_add_to_pool, handle_find_missing_files, handle_show_result
        left_args = SimpleNamespace(**{
            'job_dir': args.job_dir,
            'job_name': args.job_name,
            'dir': args.left
        })
        handle_add_to_pool(left_args, side='left')
        # 3. add-to-right
        right_args = SimpleNamespace(**{
            'job_dir': args.job_dir,
            'job_name': args.job_name,
            'dir': args.right
        })
        handle_add_to_pool(right_args, side='right')
        # 4. find-missing-files
        find_args = SimpleNamespace(**{
            'job_dir': args.job_dir,
            'job_name': args.job_name,
            'threads': args.threads,
            'no_progress': args.no_progress,
            'left': False,
            'right': False,
            'both': True
        })
        handle_find_missing_files(find_args)
        # 5. show-result
        show_args = SimpleNamespace(**{
            'job_dir': args.job_dir,
            'job_name': args.job_name,
            'summary': args.summary or not args.full_report,
            'full_report': args.full_report,
            'output': args.output,
            'show': args.show
        })
        handle_show_result(show_args)
        return 0
    elif args.command == 'import-checksums':
        from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir, get_checksum_db_path
        from dedup_file_tools_compare.phases.import_checksum import run_import_checksums
        db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
        checksum_db_path = get_checksum_db_path(args.job_dir)
        other_db_path = args.other_db
        return run_import_checksums(db_path, checksum_db_path, other_db_path)
    if args.command == 'init':
        db_path = os.path.join(args.job_dir, f"{args.job_name}.db")
        init_db(db_path)
        print(f"Initialized compare job DB at {db_path}")
        return 0
    elif args.command == 'add-to-left':
        from dedup_file_tools_compare.handler import handle_add_to_pool
        handle_add_to_pool(args, side='left')
        return 0
    elif args.command == 'add-to-right':
        from dedup_file_tools_compare.handler import handle_add_to_pool
        handle_add_to_pool(args, side='right')
        return 0
    elif args.command == 'find-missing-files':
        from dedup_file_tools_compare.handler import handle_find_missing_files
        handle_find_missing_files(args)
        return 0
    elif args.command == 'show-result':
        from dedup_file_tools_compare.handler import handle_show_result
        handle_show_result(args)
        return 0
    elif args.command == 'import-checksums':
        from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir, get_checksum_db_path
        from dedup_file_tools_compare.phases.import_checksum import run_import_checksums
        db_path = get_db_path_from_job_dir(args.job_dir, args.job_name)
        checksum_db_path = get_checksum_db_path(args.job_dir)
        other_db_path = args.other_db
        return run_import_checksums(db_path, checksum_db_path, other_db_path)
    else:
        print("Unknown command")
        return 1


def main(argv=None):
    args = parse_args(argv)
    # Set up logging using the shared commons function
    job_dir = getattr(args, 'job_dir', None)
    log_level = getattr(args, 'log_level', None)
    # Default to WARNING if not specified
    if not log_level:
        log_level = 'WARNING'
    setup_logging(log_level=log_level, job_dir=job_dir)
    logging.info(f"[COMPARE][MAIN] main() called with args: {argv}")
    code = run_main_command(args)
    logging.info(f"[COMPARE][MAIN] Main command phase complete with result: {code}")
    sys.exit(code)

if __name__ == "__main__":
    logging.info("[COMPARE][MAIN] Program started.")
    try:
        main()
    except Exception as e:
        logging.exception(f"[COMPARE][MAIN] Unhandled exception: {e}")
        sys.exit(1)
