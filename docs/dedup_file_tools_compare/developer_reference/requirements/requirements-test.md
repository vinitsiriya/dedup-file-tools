# Test Requirements: dedup_file_tools_compare

- Must have tests for each phase (add_to_pool, ensure_pool_checksums, compare, show_result).
- Must have CLI workflow tests covering all commands and output formats.
- Must test edge cases: empty dirs, large trees, identical/different/missing files.
- Must test CSV and JSON output for correctness.
- All tests must pass before release.
