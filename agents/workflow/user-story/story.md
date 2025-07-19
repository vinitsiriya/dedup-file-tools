# User Story: Pool Provenance and Path Preservation

## As a user of the deduplication tool,
I want every file's origin pool to be tracked and preserved in the database,
so that I can audit, report, and restore files with full provenance and avoid collisions when moving duplicates.

### Acceptance Criteria
- Each file scanned by `analyze` records its pool path (`pool_base_path`) in the database.
- When moving duplicates, the tool preserves the relative path to `pool_base_path` in the removal directory.
- No collisions occur when files with the same name exist in different pools.
- The workflow and CLI remain simple.
- The feature is fully tested and documented.
