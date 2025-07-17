import os

def get_db_path_from_job_dir(job_dir, job_name):
    """Return the path to the main job database given the job directory and job name."""
    return os.path.join(job_dir, f'{job_name}.db')

def get_checksum_db_path(job_dir, checksum_db=None):
    """Return the path to the checksum database, using a custom path if provided."""
    if checksum_db:
        return checksum_db
    return os.path.join(job_dir, 'checksum-cache.db')

