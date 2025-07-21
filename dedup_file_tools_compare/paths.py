import os
import datetime
from dedup_file_tools_commons.utils.logging_config import setup_logging

def get_db_path(job_dir, job_name):
    return os.path.join(job_dir, f"{job_name}.db")

def get_csv_path(job_dir, filename="compare_summary.csv"):
    return os.path.join(job_dir, filename)

def get_logs_dir(job_dir):
    logs_dir = os.path.join(job_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_log_file(job_dir):
    logs_dir = get_logs_dir(job_dir)
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    return os.path.join(logs_dir, f"compare_{timestamp}.log")

def setup_logging_for_job(job_dir, log_level='INFO', log_file=None):
    # Use the shared setup_logging from commons
    setup_logging(job_dir=job_dir, log_level=log_level)
