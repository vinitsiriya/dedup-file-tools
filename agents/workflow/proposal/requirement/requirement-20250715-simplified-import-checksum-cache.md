# Proposal: Simplify and Standardize Import Feature for Checksum Cache

## Motivation
To ensure clarity, robustness, and future compatibility, the import feature should only support importing from the `checksum_cache` table of another database with the same schema. Legacy import from `source_files` or `destination_files` is deprecated and should be removed. The CLI should use `--other-db` instead of `--old-db` for clarity.

## Requirements
- The import feature only supports importing from the `checksum_cache` table of another database with the same schema.
- Remove support for importing from `source_files` or `destination_files`.
- The CLI argument must be `--other-db` (not `--old-db`).
- The tool must validate that the other database has a compatible `checksum_cache` table and provide a clear error if not.
- Documentation and CLI help text must be updated to reflect this single, standard import method.

## Acceptance Criteria
- Users can import checksums only from the `checksum_cache` table of another compatible database.
- The CLI uses `--other-db` for the import source.
- Legacy import logic and documentation are removed.
- The tool provides clear feedback if the import source is incompatible.

---

*This proposal ensures a single, robust, and future-proof import path for checksum data.*
