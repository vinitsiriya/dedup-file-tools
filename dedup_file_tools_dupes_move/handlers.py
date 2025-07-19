import logging
from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir, get_checksum_db_path
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
from dedup_file_tools_dupes_move.db import init_db

def handle_init(job_dir, job_name):
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    checksum_db_path = get_checksum_db_path(job_dir)
    import os
    os.makedirs(job_dir, exist_ok=True)
    init_db(db_path)
    connect_with_attached_checksum_db(db_path, checksum_db_path)
    logging.info(f'Initialized job directory and database: {db_path}')


def handle_add_to_lookup_pool(job_dir, job_name, lookup_pool_root):
    # For now, treat add-to-lookup-pool as a no-op or log, as pool management is not implemented in dedup_move
    logging.info(f'add-to-lookup-pool: no operation (all pools are handled in analyze phase, lookup_pool_root={lookup_pool_root})')

def handle_analyze(job_dir, job_name, dupes_folder, threads=4):
    from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir
    from dedup_file_tools_dupes_move.phases.analysis import find_and_queue_duplicates
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    find_and_queue_duplicates(db_path, dupes_folder, threads=threads)
    logging.info(f'Analyze phase complete for dupes_folder={dupes_folder}')

def handle_preview_summary(job_dir, job_name):
    from dedup_file_tools_dupes_move.phases.preview_summary import preview_summary
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    preview_summary(db_path)

def handle_move(job_dir, job_name, dupes_folder, removal_folder, threads=4):
    from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir
    from dedup_file_tools_dupes_move.phases.move import move_duplicates
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    move_duplicates(db_path, dupes_folder, removal_folder, threads=threads)
    logging.info(f'Move phase complete for dupes_folder={dupes_folder} to removal_folder={removal_folder}')

def handle_verify(job_dir, job_name, dupes_folder, removal_folder, threads=4):
    from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir
    from dedup_file_tools_dupes_move.phases.verify import verify_moves
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    verify_moves(db_path, removal_folder, threads=threads)
    logging.info(f'Verify phase complete for dupes_folder={dupes_folder} to removal_folder={removal_folder}')

def handle_summary(job_dir, job_name):
    from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir
    from dedup_file_tools_dupes_move.phases.summary import summary_report
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    summary_report(db_path, job_dir)
    logging.info(f'Summary phase complete for job_dir={job_dir}')

def handle_one_shot(job_dir, job_name, dupes_folder, removal_folder, threads=4):
    handle_init(job_dir, job_name)
    handle_analyze(job_dir, job_name, dupes_folder, threads=threads)
    handle_preview_summary(job_dir, job_name)
    handle_move(job_dir, job_name, dupes_folder, removal_folder, threads=threads)
    handle_verify(job_dir, job_name, dupes_folder, removal_folder, threads=threads)
    handle_summary(job_dir, job_name)
    logging.info('One-shot workflow complete.')
