# dedup_file_tools_fs_copy: Skeleton Docstring Reference

This document provides a detailed reference for the skeleton docstrings and code structure of the `dedup_file_tools_fs_copy` module. It is intended to help developers and agents quickly understand the responsibilities, design goals, and main entry points of each component.

---

## Directory Structure

- **dedup_file_tools_fs_copy/**
  - `__init__.py`: Module init
  - `db.py`: Database helpers for job DB initialization and schema management
  - `main.py`: Main CLI logic, argument parsing, and handler dispatch
  - `phases/`: Phase-based logic for each major workflow step
    - `analysis.py`: Directory scanning and metadata extraction
    - `checksum.py`: Batch checksum computation and update
    - `copy.py`: File copy orchestration, deduplication, and status tracking
    - `ensure_destination_pool.py`: Ensures destination pool checksums are up to date
    - `import_checksum.py`: Imports checksums from other jobs/databases
    - `summary.py`: Generates summary reports and CSV outputs
    - `verify.py`: Shallow and deep verification of copied files
  - `utils/`: Utility modules
    - `config_loader.py`: YAML config loading and CLI merge
    - `destination_pool.py`: Destination pool index management
    - `destination_pool_cli.py`: CLI helpers for destination pool
    - `interactive_config.py`: Interactive config generator

---

## Key File Responsibilities & Docstring Summaries

### db.py
- **Purpose:** Initialization and schema management for the file copy job database.
- **Design:** Robust, resumable, auditable; safe concurrent access; extensible schema.
- **Key Function:**
  - `init_db(db_path)`: Creates tables and indexes for source, destination, and copy status.

### main.py
- **Purpose:** Main CLI entry, argument parsing, and handler dispatch for all phases.
- **Design:** Modular, extensible, supports all workflow phases and commands.
- **Key Functions:**
  - `main(args)`: Main entry point
  - `parse_args(args)`: Argument parsing
  - Handler functions for each phase (e.g., `handle_analyze`, `handle_copy`, `handle_verify`, etc.)

### phases/analysis.py
- **Purpose:** Scans directories, extracts file metadata, persists to DB.
- **Design:** Accurate, efficient, extensible for future metadata.
- **Key Functions:**
  - `persist_file_metadata(db_path, table, file_info)`
  - `scan_file_on_directory(directory_root, uid_path)`
  - `analyze_directories(db_path, directory_roots, table)`

### phases/checksum.py
- **Purpose:** Computes/updates checksums for all files in a table, stores in shared DB.
- **Design:** High-performance, thread-safe, robust error handling.
- **Key Function:**
  - `run_checksum_table(db_path, checksum_db_path, table, threads, no_progress)`

### phases/copy.py
- **Purpose:** Orchestrates file copying, deduplication, status tracking, error handling.
- **Design:** Multi-threaded, resumable, robust, audit-friendly.
- **Key Functions:**
  - `reset_status_for_missing_files(db_path, dst_roots)`
  - `get_pending_copies(db_path)`
  - `mark_copy_status(db_path, uid, rel_path, status, error_message)`
  - `copy_files(db_path, src_roots, dst_roots, threads)`

### phases/ensure_destination_pool.py
- **Purpose:** Ensures all destination pool files have up-to-date checksums.
- **Design:** Robust, efficient, idempotent.
- **Key Function:**
  - `ensure_destination_pool_checksums(job_dir, job_name, checksum_db)`

### phases/import_checksum.py
- **Purpose:** Imports checksums from another job or DB into the current job's cache.
- **Design:** Efficient, safe, idempotent, supports large-scale imports.
- **Key Function:**
  - `run_import_checksums(db_path, checksum_db_path, other_db_path)`

### phases/summary.py
- **Purpose:** Generates summary report, statistics, error details, CSV output.
- **Design:** Clear, actionable, machine-readable, extensible.
- **Key Function:**
  - `summary_phase(db_path, job_dir)`

### phases/verify.py
- **Purpose:** Shallow and deep verification of copied files (existence, size, mtime, checksum).
- **Design:** Reliable, parallel, audit-friendly, unified interface.
- **Key Functions:**
  - `verify_files(db_path, stage, reverify)`
  - `shallow_verify_files(db_path, reverify, max_workers)`
  - `deep_verify_files(db_path, reverify, max_workers)`

### utils/config_loader.py
- **Purpose:** Loads YAML config and merges with CLI args.
- **Key Functions:**
  - `load_yaml_config(config_path)`
  - `merge_config_with_args(args, config_dict, parser)`

### utils/destination_pool.py
- **Purpose:** Manages destination pool index for duplicate detection (by uid/relpath).
- **Key Class:**
  - `DestinationPoolIndex`

### utils/destination_pool_cli.py
- **Purpose:** CLI helpers for destination pool index management.
- **Key Function:**
  - `add_to_destination_index_pool(db_path, dst_root)`

### utils/interactive_config.py
- **Purpose:** Interactive config generator for user-friendly setup.
- **Key Function:**
  - `interactive_config_generator()`

---



Directory Structure:

./
.skpy-docstrings/
    dedup_file_tools_fs_copy/
        __init__.skpy
        db.skpy
        main.skpy
        phases/
            __init__.skpy
            analysis.skpy
            checksum.skpy
            copy.skpy
            ensure_destination_pool.skpy
            import_checksum.skpy
            summary.skpy
            verify.skpy
        utils/
            __init__.skpy
            config_loader.skpy
            destination_pool.skpy
            destination_pool_cli.skpy
            interactive_config.skpy
File Contents:
==========.skpy-docstrings\dedup_file_tools_fs_copy\db.skpy:
"""Database helpers for dedup_file_tools_fs_copy.

Purpose:
    Provides initialization and schema management for the file copy job database. Ensures all required tables and indexes are present for tracking source files, destination files, and copy status.

Design Goals:
    - Robust, resumable, and auditable copy workflows
    - Safe concurrent access using RobustSqliteConn
    - Extensible schema for future features"""

from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def init_db(db_path):
    """Initialize the job database for the file copy workflow.

    Args:
        db_path (str): Path to the SQLite database file.

    Implementation:
        - Creates tables for source_files, destination_files, and copy_status if they do not exist.
        - Sets up indexes for efficient lookup and status tracking.
        - Uses RobustSqliteConn for safe concurrent access.
        - Designed to be idempotent and safe to call multiple times."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\main.skpy:
from dedup_file_tools_commons.utils.logging_config import setup_logging
from dedup_file_tools_commons.db import init_checksum_db
import argparse
import logging
import sys
import os
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from pathlib import Path
from dedup_file_tools_fs_copy.db import init_db
from dedup_file_tools_fs_copy.phases.analysis import analyze_directories
from dedup_file_tools_fs_copy.phases.copy import copy_files
from dedup_file_tools_fs_copy.phases.verify import (
    shallow_verify_files,
    deep_verify_files,
)
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.paths import (
    get_db_path_from_job_dir,
    get_checksum_db_path,
)
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db


def handle_add_to_destination_index_pool(args):
    pass


def init_job_dir(job_dir, job_name, checksum_db):
    pass


def add_file_to_db(db_path, file_path):
    pass


def add_source_to_db(db_path, src_dir):
    pass


def list_files_in_db(db_path):
    pass


def remove_file_from_db(db_path, file_path):
    pass


def parse_args(args):
    pass


def main(args):
    pass


def handle_summary(args):
    pass


def handle_init(args):
    pass


def handle_analyze(args):
    pass


def handle_copy(args):
    pass


def handle_verify(args):
    pass


def handle_resume(args):
    pass


def handle_status(args):
    pass


def handle_log(args):
    pass


def handle_deep_verify(args):
    pass


def handle_verify_status(args):
    pass


def handle_deep_verify_status(args):
    pass


def handle_add_file(args):
    pass


def handle_add_source(args):
    pass


def handle_list_files(args):
    pass


def handle_remove_file(args):
    pass


def handle_checksum(args):
    pass


def handle_import_checksums(args):
    pass


def run_main_command(args):
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\analysis.skpy:
"""Analysis phase for dedup_file_tools_fs_copy.

Purpose:
    Scans source or destination directories, extracts file metadata, and persists it to the job database. Supports efficient, resumable, and auditable workflows for file copy operations.

Design Goals:
    - Accurate and efficient directory scanning
    - Robust metadata extraction and storage
    - Extensible for future metadata fields or analysis logic"""

import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from pathlib import Path
import os
from tqdm import tqdm


def persist_file_metadata(db_path, table, file_info):
    """Persist file metadata to the specified table in the job database.

    Args:
        db_path (str): Path to the job database.
        table (str): Table name ('source_files' or 'destination_files').
        file_info (dict): File metadata (uid, relative_path, size, last_modified, etc.).

    Implementation:
        - Inserts or updates the file metadata in the specified table.
        - Ensures idempotency and safe concurrent access."""
    pass


def scan_file_on_directory(directory_root, uid_path):
    """Recursively scan a directory and yield file metadata for each file found.

    Args:
        directory_root (str): Root directory to scan.
        uid_path (UidPathUtil): UidPath utility for UID/relative path abstraction.

    Yields:
        dict: File metadata for each discovered file.

    Implementation:
        - Walks the directory tree from the root.
        - For each file, extracts metadata and yields it for persistence."""
    pass


def _extract_file_info(file, uid_path):
    """Extract metadata for a single file using UidPath abstraction.

    Args:
        file (Path): File to extract info from.
        uid_path (UidPathUtil): UidPath utility for UID/relative path abstraction.

    Returns:
        dict: File metadata (uid, relative_path, size, last_modified, etc.).

    Implementation:
        - Computes UID and relative path for the file.
        - Gathers size, last modified time, and other relevant metadata."""
    pass


def analyze_directories(db_path, directory_roots, table):
    """Analyze one or more directories and persist file metadata to the job database.

    Args:
        db_path (str): Path to the job database.
        directory_roots (list[str]): List of root directories to scan.
        table (str): Table name to persist metadata ('source_files' or 'destination_files').

    Implementation:
        - Iterates over all directory roots.
        - Scans each directory and persists file metadata using persist_file_metadata.
        - Uses tqdm for progress reporting.
        - Handles errors and logs issues as needed."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\checksum.skpy:
"""Checksum phase for dedup_file_tools_fs_copy.

Purpose:
    Computes or updates checksums for all files in the specified table (e.g., source_files or destination_files) and stores them in the shared checksum database. Supports efficient, parallel, and resumable checksum operations.

Design Goals:
    - High-performance, thread-safe batch checksumming
    - Robust error handling and progress feedback
    - Consistent use of shared checksum cache for deduplication and validation"""

from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sqlite3


def run_checksum_table(db_path, checksum_db_path, table, threads, no_progress):
    """Compute or update checksums for all files in the given table (source_files or destination_files).

    Args:
        db_path (str): Path to the job database.
        checksum_db_path (str): Path to the shared checksum database.
        table (str): Table name to process ('source_files' or 'destination_files').
        threads (int): Number of worker threads to use.
        no_progress (bool): If True, disables progress bar output.

    Implementation:
        - Loads file list from the specified table in the job database.
        - Uses ThreadPoolExecutor to parallelize checksum computation, with each thread using its own DB connection.
        - Updates the checksum cache in the shared commons DB.
        - Reports progress using tqdm if enabled.
        - Handles errors and logs any issues encountered during processing."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\copy.skpy:
"""File: dedup_file_tools_fs_copy/phases/copy.py
Phase: Copy

Purpose:
    Orchestrates the copying of files from source to destination directories, ensuring deduplication, resumability, and robust error handling. Tracks copy status in the database, uses checksums to avoid redundant copies, and supports multi-threaded execution for performance.

Key Features:
    - Resets status for files missing from destination but marked as done
    - Identifies pending or failed copy tasks from the database
    - Performs deduplicated, resumable file copy operations with checksum verification
    - Updates copy status and destination file records in the database
    - Supports multi-threaded copying with progress reporting

Design Goals:
    - Deduplication, resumability, auditability, and robust error handling
    - Efficient, thread-safe database access and progress feedback"""

from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.fileops import copy_file
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
import threading
import logging


def reset_status_for_missing_files(db_path, dst_roots):
    """For any file marked as done but missing from all destination roots, reset its status to 'pending'.

    Args:
        db_path (str): Path to the job database.
        dst_roots (list[str]): List of destination root directories.

    Implementation:
        - Scans the database for files marked as 'done'.
        - Checks if the file exists in any of the destination roots.
        - If missing, updates the status in the database to 'pending' for retry.
        - Uses ThreadPoolExecutor for parallel checks and tqdm for progress feedback.
        - Updates are performed sequentially to avoid DB locking."""
    pass


def get_pending_copies(db_path):
    """Returns a list of files that are pending, in error, or in progress for copying.

    Args:
        db_path (str): Path to the job database.

    Returns:
        list[tuple]: List of (uid, relative_path, size, last_modified) for files to be copied.

    Implementation:
        - Queries the database for files whose copy status is NULL, 'pending', 'error', or 'in_progress'.
        - Returns a list of tuples for further processing by the copy phase."""
    pass


def mark_copy_status(db_path, uid, rel_path, status, error_message):
    """Updates the copy status for a file in the database.

    Args:
        db_path (str): Path to the job database.
        uid (str): Unique file identifier.
        rel_path (str): Relative file path.
        status (str): New status ('pending', 'done', 'error', etc.).
        error_message (str, optional): Error message if status is 'error'.

    Implementation:
        - Inserts or updates the copy_status table for the given file (uid, rel_path).
        - Records the new status, timestamp, and any error message.
        - Ensures resumability and accurate tracking of copy progress and errors."""
    pass


def copy_files(db_path, src_roots, dst_roots, threads):
    """Orchestrates the multi-threaded copying of files from source to destination, with deduplication and status tracking.

    Args:
        db_path (str): Path to the job database.
        src_roots (list[str]): List of source root directories.
        dst_roots (list[str]): List of destination root directories.
        threads (int): Number of worker threads to use.

    Implementation:
        - Resets status for missing files before starting.
        - Loads pending copy tasks from the database.
        - For each file:
            - Checks if the file is already present at the destination (by checksum and path).
            - If not, copies the file, verifies checksum, and updates the database.
            - Handles errors and updates status accordingly.
        - Uses ThreadPoolExecutor for parallelism and tqdm for progress reporting.
        - Ensures robust, resumable, and deduplicated copy operations.
        - All operations are logged and errors are handled per file."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\ensure_destination_pool.skpy:
"""Ensures that all files in the destination pool have up-to-date checksums in the shared checksum database.

Purpose:
    - Scans the destination pool for all files tracked in the job database.
    - Computes or loads checksums for each file and updates the checksum cache as needed.
    - Ensures deduplication and verification logic can rely on complete checksum data for all destination files.

Design Goals:
    - Robust, resumable, and auditable checksum management for destination pools
    - Efficient batch processing and progress feedback
    - Safe concurrent database access"""

from dedup_file_tools_commons.utils.paths import (
    get_db_path_from_job_dir,
    get_checksum_db_path,
)
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from tqdm import tqdm
import logging


def ensure_destination_pool_checksums(job_dir, job_name, checksum_db):
    """Ensure all files in the destination pool have checksums in the shared checksum database.

    Args:
        job_dir (str): Path to the job directory.
        job_name (str): Name of the job.
        checksum_db (str): Path to the shared checksum database.

    Implementation:
        - Loads the list of destination files from the job database.
        - For each file, checks if a checksum exists in the cache; if not, computes and stores it.
        - Uses tqdm for progress reporting.
        - Handles errors and logs any issues encountered during processing.
        - Designed to be idempotent and safe to call multiple times."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\import_checksum.skpy:
"""Import checksums phase for dedup_file_tools_fs_copy.

Purpose:
    Imports checksum data from another job or external database into the current job's checksum cache. Enables reuse of previously computed checksums for faster, deduplicated copy operations.

Design Goals:
    - Efficient, safe, and idempotent import of checksum data
    - Robust error handling and progress feedback
    - Support for large-scale imports and cross-job deduplication"""

from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
from tqdm import tqdm
import logging
import sys


def run_import_checksums(db_path, checksum_db_path, other_db_path):
    """Import checksums from another database into the current job's checksum cache.

    Args:
        db_path (str): Path to the current job database.
        checksum_db_path (str): Path to the shared checksum database.
        other_db_path (str): Path to the external or previous job's database to import from.

    Implementation:
        - Attaches the other database and reads checksum data.
        - Inserts or updates checksums in the current job's checksum cache.
        - Uses tqdm for progress reporting.
        - Handles errors and logs any issues encountered during import.
        - Designed to be idempotent and safe for repeated use."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\summary.skpy:
"""Summary phase for dedup_file_tools_fs_copy.

Purpose:
    Generates a summary report of the copy job, including statistics, error details, and output locations for logs and reports. Supports both console and CSV output for easy review and automation.

Design Goals:
    - Clear, actionable reporting for end users
    - Machine-readable output for automation and audit
    - Extensible for future reporting needs"""

import os
import csv
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def summary_phase(db_path, job_dir):
    """Print a summary of the copy job and generate a CSV report of errors and incomplete files.

    Args:
        db_path (str): Path to the job database.
        job_dir (str): Path to the job directory (for output files and logs).

    Implementation:
        - Queries the database for job statistics (total files, done, errors, pending, etc.).
        - Prints a summary to the console, including log file locations.
        - Generates a CSV report listing files with errors or not marked as done.
        - Designed for both human and machine consumption."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\phases\verify.skpy:
"""Verification phase for dedup_file_tools_fs_copy.

Purpose:
    Provides both shallow and deep verification of copied files. Shallow verification checks file existence, size, and timestamps; deep verification also compares checksums. Supports multithreaded execution and resumable verification.

Design Goals:
    - Reliable, auditable verification of copy results
    - Efficient, parallel verification for large datasets
    - Unified interface for both shallow and deep verification"""

import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
import time
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPath, UidPathUtil


def verify_files(db_path, stage, reverify):
    """Unified verify function: runs shallow or deep verification based on stage.

    Args:
        db_path (str): Path to job database.
        stage (str): 'shallow' or 'deep'.
        reverify (bool): If True, clear previous verification results before running.

    Implementation:
        - Dispatches to shallow or deep verification as requested.
        - Handles clearing of previous results if reverify is True.
        - Logs progress and errors."""
    pass


def shallow_verify_files(db_path, reverify, max_workers):
    """Shallow verification: check file existence, size, and last modified time. Supports multithreading.

    Args:
        db_path (str): Path to job database.
        reverify (bool): If True, clear previous verification results before running.
        max_workers (int): Number of worker threads to use.

    Implementation:
        - Checks each file for existence, size, and mtime.
        - Uses ThreadPoolExecutor for parallelism.
        - Updates verification status in the database.
        - Logs progress and errors."""
    pass


def deep_verify_files(db_path, reverify, max_workers):
    """Deep verification: always perform all shallow checks, then compare checksums. Supports multithreading.

    Args:
        db_path (str): Path to job database.
        reverify (bool): If True, clear previous verification results before running.
        max_workers (int): Number of worker threads to use.

    Implementation:
        - Performs all shallow checks.
        - Computes and compares checksums for each file.
        - Uses ThreadPoolExecutor for parallelism.
        - Updates verification status in the database.
        - Logs progress and errors."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\utils\config_loader.skpy:
import yaml
import argparse
import os


def load_yaml_config(config_path):
    pass


def merge_config_with_args(args, config_dict, parser):
    """Update the argparse.Namespace `args` with values from config_dict,
    but only for arguments that are still set to their default values.
    CLI args always take precedence."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\utils\destination_pool.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
import time


class DestinationPoolIndex:
    """Manages the destination pool index for global duplicate detection.
    This does NOT store checksums, only tracks which files are in the pool (by uid and relative path).
    Checksum management remains in checksum_cache.py."""

    def __init__(self, uid_path):
        pass

    def add_or_update_file(self, conn, path, size, last_modified):
        pass

    def exists(self, conn, uid, rel_path):
        pass

    def all_files(self, conn):
        pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\utils\destination_pool_cli.skpy:
import logging
from pathlib import Path
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from .destination_pool import DestinationPoolIndex


def add_to_destination_index_pool(db_path, dst_root):
    """Recursively scan dst_root and add/update all files in the destination pool index."""
    pass


==========.skpy-docstrings\dedup_file_tools_fs_copy\utils\interactive_config.skpy:
import yaml
import os


def interactive_config_generator():
    pass


## How to Use This Reference

- Use this outline to quickly locate the relevant skeleton docstring or function for any workflow phase or utility.
- Refer to the `.skpy` files for detailed docstrings and function/class signatures.
- For implementation, see the mapped Python files in the main codebase.

---

_Last updated: 2025-07-21_
