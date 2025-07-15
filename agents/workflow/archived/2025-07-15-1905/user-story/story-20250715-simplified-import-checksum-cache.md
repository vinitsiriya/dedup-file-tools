# User Story: Simplified and Standardized Checksum Import

## Context
As a user, I want to import checksums from the `checksum_cache` table of another compatible database, so that migration and deduplication are robust, simple, and future-proof, and I am not confused by legacy or multiple import paths.

## Scenario
- The CLI provides an `import-checksums` command that only accepts `--other-db` (path to another compatible database).
- The tool imports all valid checksums from the `checksum_cache` table of the other database into the current job's `checksum_cache`.
- The tool validates schema compatibility and provides a clear error if the other database is not compatible.
- The tool does not support importing from `source_files` or `destination_files`.
- Documentation and CLI help text are updated to reflect this single, standard import method.

## Acceptance Criteria
- Users can import checksums only from the `checksum_cache` table of another compatible database using `--other-db`.
- The tool provides clear feedback if the import source is incompatible.
- No legacy import options or documentation remain.
- The import process is robust, idempotent, and auditable.

---

Linked requirement: requirement-20250715-simplified-import-checksum-cache.md
