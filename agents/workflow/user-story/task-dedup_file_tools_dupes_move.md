# Tasks: dedup_file_tools_dupes_move

- [ ] Design package structure and create initial files (`__init__.py`, `cli.py`, etc.)
- [ ] Identify and migrate the following common utilities from `dedup_file_tools_fs_copy/utils/` to `dedup_file_tools_commons` (using IDE, not agent):
    - `uidpath.py`
    - `checksum_cache.py`
    - `robust_sqlite.py`
    - `logging_config.py`
    - `fileops.py`
  Update all imports in both packages to use the new commons package. Test both packages after migration to ensure correctness.
- [ ] Implement recursive directory scan and checksum calculation
- [ ] Group files by checksum and identify duplicates
- [ ] Implement logic to move all but one file per duplicate group to destination
- [ ] Implement dry-run mode
- [ ] Implement resumability and idempotency (move log or state DB)
- [ ] Implement CLI with all required options and subcommands
- [ ] Implement logging and audit trail features
- [ ] Write unit and integration tests (including edge cases)
- [ ] Update documentation and strategy notes
- [ ] Perform code review and refactor as needed
- [ ] Archive planning and strategy files as per workflow protocol
