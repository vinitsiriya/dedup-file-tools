# copy.md - Requirements Documentation for copy.py

## Purpose
This module implements the copy phase of the file copy workflow. It is responsible for copying files from source to destination, ensuring data integrity, deduplication, and robust error handling.

## Key Requirements

### 1. Pending File Selection
- The tool must select files marked as pending, error, or in-progress in the job database for copying.
- It must skip files already marked as done or already present in the destination with the correct checksum.

### 2. UID/Path Resolution
- For each file, the absolute source path must be reconstructed using UidPath.reconstruct_path(uid, rel_path).
- The destination path must be constructed as `dst_root / rel_path`, mirroring the structure from the mount point.

### 3. Directory Creation
- The tool must ensure that all parent directories for the destination file exist before copying.
- Directory creation must be robust to race conditions and cross-platform issues.

### 4. File Copy and Verification
- The tool must copy the file in blocks, optionally showing progress.
- After copying, it must verify the checksum of the destination file matches the source.
- The tool must update the job database with the result (done or error).

### 5. Deduplication and Resume
- The tool must avoid redundant copies by checking checksums and copy status.
- It must support resuming incomplete jobs and skipping already copied files.

### 6. Threading and Concurrency
- The copy phase must support multi-threaded copying, with a configurable number of threads.
- It must wait for all threads to finish before returning.

### 7. Error Handling and Logging
- All errors must be logged and reported in the job database.
- The tool must provide detailed debug output for each file operation.

### 8. Testability
- The copy phase must be unit- and integration-testable, with tests verifying correct file placement, status updates, and error handling.

---

This document describes the requirements and design intent for `copy.py` in the file copy tool. Each requirement is traceable to a specific function or workflow step in the implementation.
