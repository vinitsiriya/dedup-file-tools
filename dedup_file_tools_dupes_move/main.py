

import argparse
import logging
from dedup_file_tools_commons.utils.logging_config import setup_logging
from dedup_file_tools_dupes_move.utils.config_loader import load_yaml_config, merge_config_with_args
from dedup_file_tools_dupes_move.handlers import (
    handle_init, handle_add_to_lookup_pool, handle_analyze, handle_preview_summary,
    handle_move, handle_verify, handle_summary, handle_one_shot
)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Deduplication/dupes remover tool: scan, group, and move duplicates.")
    parser.add_argument('--log-level', default='INFO', help='Logging level')
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
    parser_move.add_argument('--lookup-pool', required=True, help='Source folder to scan for duplicates (dupes folder)')
    parser_move.add_argument('--dupes-folder', required=True, help='Folder to move duplicates into (removal folder)')
    parser_move.add_argument('--threads', type=int, default=4, help='Number of threads for move phase')

    parser_verify = subparsers.add_parser('verify', help='Verify that duplicates were moved/removed as planned')
    parser_verify.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_verify.add_argument('--job-name', required=True, help='Name for this deduplication job')
    parser_verify.add_argument('--lookup-pool', required=True, help='Source folder to scan for duplicates (dupes folder)')
    parser_verify.add_argument('--dupes-folder', required=True, help='Folder where duplicates should have been moved (removal folder)')
    parser_verify.add_argument('--threads', type=int, default=4, help='Number of threads for verify phase')

    parser_summary = subparsers.add_parser('summary', help='Print summary and generate CSV report of deduplication results')
    parser_summary.add_argument('--job-dir', required=True, help='Directory to store job state and database')
    parser_summary.add_argument('--job-name', required=True, help='Name for this deduplication job')

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
    setup_logging(args.job_dir, args.log_level)

    if args.command == 'init':
        handle_init(args.job_dir, args.job_name)
    elif args.command == 'add-to-lookup-pool':
        handle_add_to_lookup_pool(args.job_dir, args.job_name, args.lookup_pool)
    elif args.command == 'analyze':
        handle_analyze(args.job_dir, args.job_name, args.lookup_pool, threads=args.threads)
    elif args.command == 'preview-summary':
        handle_preview_summary(args.job_dir, args.job_name)
    elif args.command == 'move':
        # For test and CLI, use lookup_pool as source and dupes_folder as destination
        handle_move(args.job_dir, args.job_name, args.lookup_pool, args.dupes_folder, threads=args.threads)
    elif args.command == 'verify':
        handle_verify(args.job_dir, args.job_name, args.lookup_pool, args.dupes_folder, threads=args.threads)
    elif args.command == 'summary':
        handle_summary(args.job_dir, args.job_name)
    elif args.command == 'one-shot':
        handle_one_shot(args.job_dir, args.job_name, args.lookup_pool, args.dupes_folder, threads=args.threads)
    else:
        parser.print_help()
