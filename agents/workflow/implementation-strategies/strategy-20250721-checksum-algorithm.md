# Checksum Algorithm Strategy: dedup-file-tools

This document describes the checksum algorithms used in the dedup-file-tools project and their implementation in the common utilities.

## Algorithms Used

- **SHA-256**
  - The primary algorithm for file checksumming across all modules.
  - Provides strong collision resistance and is suitable for deduplication, integrity checking, and audit trails.
  - Used by default in all checksum-related operations.

- **(Legacy/Alternate) Algorithms**
  - The architecture allows for future extension to other algorithms (e.g., MD5, SHA-1) if needed for compatibility or performance, but SHA-256 is the standard.


## Efficient Batch Checksumming: Per-Thread Database Connections

For high-performance, parallel checksumming (as in `phases/checksum.py`), the following strategy is used:

- **Batch Mode:**
  - Files to be checksummed are divided into large batches (e.g., 5000+ files per batch).
  - Each batch is processed independently, reducing overhead and improving throughput.
- **Per-Thread Database Connection:**
  - Each worker thread opens its own database connection to the checksum DB (see `RobustSqliteConn`).
  - This avoids contention and locking issues that occur when sharing a single connection across threads.
  - Example: see the `process_batch` function in `dedup_file_tools_fs_copy/phases/checksum.py`.
- **ThreadPoolExecutor:**
  - Python's `ThreadPoolExecutor` is used to parallelize batch processing, with each thread handling a batch and its own DB connection.
- **Progress Reporting:**
  - Progress bars (via `tqdm`) are updated as each file is processed, providing user feedback without blocking threads.

This approach ensures that checksum computation is both thread-safe and highly efficient, even for very large file sets.

## Implementation

- The checksum calculation logic is implemented in the common utilities:
  - `dedup_file_tools_commons/utils/fileops.py` (see `compute_sha256`)
  - Used by both `ChecksumCache` and `ChecksumCache2` classes in `dedup_file_tools_commons/utils/checksum_cache.py` and `checksum_cache2.py`.
- All modules should use these shared utilities for checksumming to ensure consistency and maintainability.

## References
- [Common Utilities Structure](strategy-20250721-commons-utilities.md)
- [ChecksumCache Implementation](../../dedup_file_tools_commons/utils/checksum_cache.py)
- [ChecksumCache2 Implementation](../../dedup_file_tools_commons/utils/checksum_cache2.py)
- [FileOps Utility](../../dedup_file_tools_commons/utils/fileops.py)

---

This strategy ensures that all deduplication and integrity operations use a robust, consistent, and well-documented checksum approach across the project.
