# Global Requirements: dedup_file_tools_compare

- Must support efficient, auditable comparison of two directory trees using checksums.
- Must provide a modular, phase-based workflow (add-to-pool, ensure checksums, compare, show results).
- Must use a persistent checksum cache and SQLite DB for all operations.
- Must support multithreaded, batched processing for large trees.
- Must provide a scriptable CLI with summary, full, CSV, and JSON output.
- Must be robust to errors and large datasets.
- Must be fully testable, with per-phase and CLI workflow tests.
