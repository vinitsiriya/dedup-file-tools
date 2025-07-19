

import argparse
import logging
from dedup_file_tools_commons.utils.logging_config import setup_logging
from dedup_file_tools_dupes_move.utils.config_loader import load_yaml_config, merge_config_with_args
from dedup_file_tools_dupes_move.handlers import (
    handle_init, handle_add_to_lookup_pool, handle_analyze, handle_preview_summary,
    handle_move, handle_verify, handle_summary, handle_one_shot, handle_import_checksums
)



def main(argv=None):
    parser = argparse.ArgumentParser(description="Deduplication/dupes remover tool: scan, group, and move duplicates.")
    parser.add_argument('--log-level', default='WARNING', help='Logging level')
    parser.add_argument('--config', default=None, help='YAML config file')
    subparsers = parser.add_subparsers(dest='command')

    parser_init = subparsers.add_parser('init', help='Initialize a new deduplication job')
    parser_init.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_init.add_argument('--job-name', required=True, help='Name for this deduplication job')

    parser_add_lookup = subparsers.add_parser('add-to-lookup-pool', help='(Optional) Add a folder to the lookup pool for duplicate scanning')
    parser_add_lookup.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_add_lookup.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_add_lookup.add_argument('--lookup-pool', required=True, help='Path to folder to scan for duplicates')

    parser_analyze = subparsers.add_parser('analyze', help='Scan the lookup pool, compute checksums, and group duplicates')
    parser_analyze.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_analyze.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_analyze.add_argument('--lookup-pool', required=True, help='Path to folder to scan for duplicates')
    parser_analyze.add_argument('--threads', type=int, default=4, help='Number of threads for analysis')

    parser_preview = subparsers.add_parser('preview-summary', help='Preview planned duplicate groups and moves')
    parser_preview.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_preview.add_argument('--job-name', required=True, help='Name for this deduplication job')

    parser_move = subparsers.add_parser('move', help='Move duplicate files to the dupes folder (or remove)')
    parser_move.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_move.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_move.add_argument('--dupes-folder', required=False, help='Folder to move duplicates into (removal folder)')
    parser_move.add_argument('--threads', type=int, default=4, help='Number of threads for move phase')

    parser_verify = subparsers.add_parser('verify', help='Verify that duplicates were moved/removed as planned')
    parser_verify.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_verify.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_verify.add_argument('--threads', type=int, default=4, help='Number of threads for verify phase')

    parser_summary = subparsers.add_parser('summary', help='Print summary and generate CSV report of deduplication results')
    parser_summary.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_summary.add_argument('--job-name', required=True, help='Name for this deduplication job')

    parser_import = subparsers.add_parser('import-checksums', help='Import checksums from another compatible database')
    parser_import.add_argument('--job-dir', required=True, help='Directory to store job state and database')

    args = parser.parse_args(argv)

    # Only set up logging if job_dir is present in args
    job_dir = getattr(args, 'job_dir', None)
    log_level = getattr(args, 'log_level', 'WARNING')
    if job_dir is not None:
        setup_logging(job_dir, log_level)
    parser_import.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_import.add_argument('--other-db', required=True, help='Path to other compatible SQLite database (must have checksum_cache table)')
    parser_import.add_argument('--checksum-db', required=False, help='Custom checksum DB path (default: <job-dir>/checksum-cache.db)')

    parser_one_shot = subparsers.add_parser('one-shot', help='Run the full deduplication workflow in one command')
    parser_one_shot.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_one_shot.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_one_shot.add_argument('--lookup-pool', required=True, help='Path to folder to scan for duplicates')
    parser_one_shot.add_argument('--dupes-folder', required=True, help='Folder to move duplicates into')
    parser_one_shot.add_argument('--threads', type=int, default=4, help='Number of threads for all phases')

    import sys
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    if args.config:
        config_dict = load_yaml_config(args.config)
        args = merge_config_with_args(args, config_dict, parser)

    # Only set up logging if job_dir is present in args
    job_dir = getattr(args, 'job_dir', None)
    log_level = getattr(args, 'log_level', 'WARNING')
    if job_dir is not None:
        setup_logging(job_dir, log_level)

    def get_lookup_pool_from_db(job_dir, job_name):
        import sqlite3
        import os
        db_path = os.path.join(job_dir, f"{job_name}.db")
        if not os.path.exists(db_path):
            raise RuntimeError(f"Job database not found: {db_path}")
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM job_metadata WHERE key='lookup_pool' LIMIT 1")
            row = cur.fetchone()
            if row:
                return row[0]
            else:
                raise RuntimeError("lookup_pool not found in job_metadata. Please specify --lookup-pool.")

    if args.command == 'init':
        handle_init(args.job_dir, args.job_name)
    elif args.command == 'add-to-lookup-pool':
        handle_add_to_lookup_pool(args.job_dir, args.job_name, args.lookup_pool)
    elif args.command == 'analyze':
        # Store lookup_pool in job_metadata for later phases
        handle_analyze(args.job_dir, args.job_name, args.lookup_pool, threads=args.threads)
        # Save lookup_pool to job_metadata
        import sqlite3, os
        db_path = os.path.join(args.job_dir, f"{args.job_name}.db")
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS job_metadata (key TEXT PRIMARY KEY, value TEXT)")
            cur.execute("INSERT OR REPLACE INTO job_metadata (key, value) VALUES (?, ?)", ("lookup_pool", args.lookup_pool))
            conn.commit()
    elif args.command == 'preview-summary':
        handle_preview_summary(args.job_dir, args.job_name)
    elif args.command == 'move':
        lookup_pool = get_lookup_pool_from_db(args.job_dir, args.job_name)
        import sqlite3, os
        db_path = os.path.join(args.job_dir, f"{args.job_name}.db")
        # If dupes_folder is not provided, load from job_metadata
        dupes_folder = args.dupes_folder
        if not dupes_folder:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute("SELECT value FROM job_metadata WHERE key='dupes_folder' LIMIT 1")
                row = cur.fetchone()
                if row:
                    dupes_folder = row[0]
                else:
                    raise RuntimeError("dupes_folder not found in job_metadata. Please specify --dupes-folder during first move phase.")
        # Save dupes_folder to job_metadata for later use
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS job_metadata (key TEXT PRIMARY KEY, value TEXT)")
            cur.execute("INSERT OR REPLACE INTO job_metadata (key, value) VALUES (?, ?)", ("dupes_folder", dupes_folder))
            conn.commit()
        handle_move(args.job_dir, args.job_name, lookup_pool, dupes_folder, threads=args.threads)
    elif args.command == 'verify':
        lookup_pool = get_lookup_pool_from_db(args.job_dir, args.job_name)
        # Load dupes_folder from job_metadata
        import sqlite3, os
        db_path = os.path.join(args.job_dir, f"{args.job_name}.db")
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM job_metadata WHERE key='dupes_folder' LIMIT 1")
            row = cur.fetchone()
            if row:
                dupes_folder = row[0]
            else:
                raise RuntimeError("dupes_folder not found in job_metadata. Please specify it during move phase.")
        handle_verify(args.job_dir, args.job_name, lookup_pool, dupes_folder, threads=args.threads)
    elif args.command == 'summary':
        handle_summary(args.job_dir, args.job_name)
    elif args.command == 'one-shot':
        handle_one_shot(args.job_dir, args.job_name, args.lookup_pool, args.dupes_folder, threads=args.threads)
    elif args.command == 'import-checksums':
        handle_import_checksums(args.job_dir, args.job_name, args.other_db, checksum_db=getattr(args, 'checksum_db', None))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()


