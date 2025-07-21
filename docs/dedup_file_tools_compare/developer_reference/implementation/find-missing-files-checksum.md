# Implementation: Find Missing Files by Comparing Two Directories Using Checksums

## Overview
This feature is implemented as a modular, phase-based workflow in the `dedup_file_tools_compare` module. It uses a persistent SQLite database and a shared checksum cache for efficient, auditable comparisons.

## Key Components
- **Database Schema:**
  - Tables for left/right pools, missing files, identical/different files, and result tables.
- **Phases:**
  - `add_to_pool`: Scans a directory, populates the pool, and updates the DB.
  - `ensure_pool_checksums`: Ensures all files in a pool have up-to-date checksums in the cache.
  - `compare`: Compares left/right pools by checksum, populates result tables for missing, identical, and different files.
  - `results`: Outputs results in summary, full, CSV, or JSON formats.
- **Concurrency:**
  - Uses ThreadPoolExecutor for parallel directory scanning and checksum calculation.
  - Batches DB operations for performance.
- **CLI:**
  - Argparse-based CLI with commands for each phase.
  - All commands are scriptable and support progress bars.
- **Testing:**
  - Per-phase and CLI workflow tests ensure correctness and robustness.

## Data Flow
1. User initializes a job and adds files to left/right pools.
2. The tool scans directories, populates the DB, and updates the checksum cache.
3. The comparison phase finds missing, identical, and different files by checksum.
4. Results are output in the requested format.

## Error Handling
- All phases handle missing files, DB errors, and checksum issues gracefully.
- Progress bars and logging provide user feedback during long operations.

## Extensibility
- The modular design allows for easy addition of new comparison strategies or output formats.
