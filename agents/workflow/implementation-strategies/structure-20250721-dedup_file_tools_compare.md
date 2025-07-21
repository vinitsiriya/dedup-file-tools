# Directory Structure: dedup_file_tools_compare

This document describes the recommended directory and file structure for the `dedup_file_tools_compare` module, inspired by the organization of `dedup_file_tools_fs_copy`.

## Structure

```
dedup_file_tools_compare/
    __init__.py
    main.py                  # CLI entry point
    handler.py
    db.py                   # (Optional) Database schema/logic for compare jobs
    phases/                 # All phase-based logic is organized here
        __init__.py
        add_to_pool.py      # Add files to left/right pools
        compare.py          # Comparison phase logic
        results.py          # Result formatting and export
        summary.py          # Summary and reporting phase
    tests/
```

- All core logic is separated for clarity and maintainability.
