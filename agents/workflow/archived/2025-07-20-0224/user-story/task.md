# Tasks: Pool Provenance and Path Preservation

- [ ] Update the database schema to add `pool_base_path` to `dedup_files_pool` (with migration logic).
- [ ] Update analysis phase to set `pool_base_path` for each file scanned.
- [ ] Update move phase to use `pool_base_path` for computing the destination path in the removal directory.
- [ ] Update or add tests to verify provenance and path preservation.
- [ ] Update documentation for users and developers.
- [ ] Ensure backward compatibility and provide migration instructions.
