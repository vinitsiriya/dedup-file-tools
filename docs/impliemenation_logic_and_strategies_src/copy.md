# Implementation Logic and Strategies: copy.py

## Overview
`copy.py` implements the copy phase of the file copy workflow. It is responsible for robust, multi-threaded copying of files from source to destination, with full support for deduplication, resume, and error handling.

## Key Implementation Strategies

### 1. Pending File Selection
- Uses `get_pending_copies` to select files from the database that are pending, in-progress, or errored.
- Skips files already marked as done or already present in the destination with the correct checksum.

### 2. UID/Path Resolution
- For each file, reconstructs the absolute source path using `UidPath.reconstruct_path(uid, rel_path)`.
- The destination path is constructed as `dst_root / rel_path`, mirroring the structure from the mount point.

### 3. Directory Creation
- Ensures all parent directories for the destination file exist before copying, using `mkdir(parents=True, exist_ok=True)`.
- Prints debug output before and after directory creation for observability.

### 4. File Copy and Verification
- Uses `copy_file` to copy the file in blocks, with optional progress reporting.
- After copying, verifies the checksum of the destination file matches the source.
- Updates the job database with the result (done or error) and logs all actions.

### 5. Deduplication and Resume
- Maintains a set of checksums already present on disk or copied in the current batch to avoid redundant copies.
- Supports resuming incomplete jobs and skipping already copied files by checking status and checksums.

### 6. Threading and Concurrency
- Uses a `ThreadPoolExecutor` to copy files in parallel, with a configurable number of threads.
- Waits for all threads to finish before returning, ensuring all copy jobs are complete.
- Uses a lock to synchronize access to shared state (e.g., deduplication set).

### 7. Error Handling and Logging
- All errors are logged and reported in the job database.
- Provides detailed debug output for each file operation, including thread name, file paths, and status.

### 8. Integration
- Integrates with `ChecksumCache` for fast lookup and deduplication.
- Designed to be called from the main CLI handler, with all arguments and state passed explicitly.

---

This document explains the implementation logic and strategies for `copy.py`, supporting maintainability, observability, and future enhancements.
