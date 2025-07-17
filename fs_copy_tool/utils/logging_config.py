import logging
import os
import datetime

def setup_logging(job_dir=None, log_level=None):
    """
    Set up logging to a timestamped log file in the job_dir/logs directory.
    If job_dir is None, use 'changes/fs_copy_tool.log'.
    log_level can be passed as a string (e.g., 'INFO', 'DEBUG').
    If not provided, will use LOG_LEVEL environment variable, or default to 'INFO'.
    """
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
    else:
        log_level = str(log_level).upper()
    numeric_level = getattr(logging, log_level, logging.WARNING)
    if job_dir:
        logs_dir = os.path.join(job_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = os.path.join(logs_dir, f'fs_copy_tool_{timestamp}.log')
    else:
        log_file = 'changes/fs_copy_tool.log'
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(numeric_level)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    import sys
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    ch.setLevel(numeric_level)
    logger.handlers = []
    logger.addHandler(fh)
    logger.addHandler(ch)
