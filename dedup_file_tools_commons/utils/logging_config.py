import logging
import os
import datetime

def setup_logging(job_dir=None, log_level=None):
    """
    Set up logging to a timestamped log file in the job_dir/logs directory.
    If job_dir is None, use 'changes/dedup_file_tools_fs_copy.log'.
    log_level can be passed as a string (e.g., 'INFO', 'DEBUG').
    If not provided, will use LOG_LEVEL environment variable, or default to 'INFO'.
    """
    # File logs: always INFO or as specified
    file_log_level = os.environ.get('FILE_LOG_LEVEL', 'INFO').upper()
    file_numeric_level = getattr(logging, file_log_level, logging.INFO)
    # Console logs: always WARNING or as specified
    console_log_level = os.environ.get('CONSOLE_LOG_LEVEL', 'WARNING').upper()
    console_numeric_level = getattr(logging, console_log_level, logging.WARNING)
    # If log_level is provided, override both
    if log_level is not None:
        file_numeric_level = console_numeric_level = getattr(logging, str(log_level).upper(), logging.INFO)
    if job_dir:
        logs_dir = os.path.join(job_dir, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        log_file = os.path.join(logs_dir, f'dedup_file_tools_{timestamp}.log')
    else:
        log_file = 'changes/dedup_file_tools_fs_copy.log'
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # Remove all handlers before adding new ones
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    class FlushFileHandler(logging.FileHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()
    fh = FlushFileHandler(log_file, encoding='utf-8')
    fh.setLevel(file_numeric_level)
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    import sys
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    ch.setLevel(console_numeric_level)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"Logging initialized. Log file: {log_file}")
    logger.error("Test error log to verify logging setup.")
