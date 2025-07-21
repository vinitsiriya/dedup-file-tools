# Directory Structure: dedup_file_tools_commons

This document describes the directory and file structure for the `dedup_file_tools_commons` module, which provides shared utilities and abstractions for the dedup-file-tools project.

## Structure

```
dedup_file_tools_commons/
    __init__.py
    db.py                      # Common database helpers and schema logic
    utils/
        __init__.py
        checksum_cache.py      # Checksum cache logic (legacy or v1)
        checksum_cache2.py     # Checksum cache logic (v2, improved)
        db_utils.py            # Database utility functions
        fileops.py             # File operations and helpers
        logging_config.py      # Logging setup and configuration
        paths.py               # Path utilities (e.g., job dir, db path helpers)
        robust_sqlite.py       # Robust SQLite connection/transaction helpers
        uidpath.py             # System-independent path abstraction (UidPath)
```

- All shared logic and utilities are placed in this module for reuse across all tools.
- The `utils/` subpackage contains focused utility modules for checksumming, file operations, database access, and path handling.
- The `uidpath.py` module provides a robust, system-independent file path abstraction for cross-platform compatibility.

---

# UidPath Utility

The `UidPath` abstraction (see `utils/uidpath.py`) enables robust, portable file referencing by converting absolute paths into a tuple of (UID, relative path), where UID is a unique identifier for the filesystem (volume serial number on Windows, UUID on Linux) and the relative path is relative to the mount point.

- **Purpose:**
  - Enables system-independent file references for backup, deduplication, and cross-platform workflows.
  - Ensures file references remain valid even if drive letters or mount points change.
- **Usage:**
  - Use `UidPathUtil().convert_path(path)` to convert a file path to (uid, rel_path).
  - Use `UidPathUtil().reconstruct_path(uid, rel_path)` to reconstruct the absolute path on the current system.
- **Best Practice:**
  - Treat the returned `rel_path` as opaque; only `UidPath` should interpret or manipulate it.

For more details and examples, see `docs/dedup_file_tools_commons/uidpath.md`.
