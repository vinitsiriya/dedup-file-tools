# Strategy: Common Utilities and Directory Structure

This document outlines the strategy for organizing and referencing shared utilities in the dedup-file-tools project, with a focus on the `dedup_file_tools_commons` module.

## Common Utilities Directory Structure

All shared logic, helpers, and abstractions are placed in the `dedup_file_tools_commons` module for maximum code reuse and maintainability. The structure is as follows:

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

- All modules and tools in the project should import shared logic from this package.
- The `utils/` subpackage is organized by function for clarity and discoverability.

## Key Document References

- [Structure of dedup_file_tools_commons](../docs/dedup_file_tools_commons/structure.md):
  - Describes the directory and file layout for all shared utilities.
- [UidPath Abstraction](../docs/dedup_file_tools_commons/uidpath.md):
  - Explains the system-independent path abstraction for robust, portable file referencing.


## Checksum Algorithm

For details on the checksum algorithm(s) used and their implementation, see:
- [Checksum Algorithm Strategy](strategy-20250721-checksum-algorithm.md)

## Best Practices

- Always use the utilities in `dedup_file_tools_commons` for checksumming, file operations, database access, and path handling.
- When adding new shared logic, place it in the appropriate module in `dedup_file_tools_commons/utils/` and update the structure documentation.
- Reference the relevant documentation in code comments and design docs to ensure maintainability and onboarding ease.

---

This strategy ensures a clean, maintainable, and well-documented foundation for all dedup-file-tools modules and workflows.
