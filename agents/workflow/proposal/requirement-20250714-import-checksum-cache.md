# Proposal: Import Checksum as Checksum Cache Holder

## Background
Currently, the `import-checksums` phase is responsible for importing and/or computing checksums for all files in the job database. This process can involve reading external checksum files, computing missing checksums, and updating the database.

## Proposal
Redefine the `import-checksums` phase to act solely as a checksum cache holder. Its responsibilities would be:

- **Hold and manage a cache of checksums** imported from external sources (e.g., .sha256 files, manifest files, or other trusted sources).
- **Do not compute or update checksums** during this phase. Only import and store externally provided checksums.
- **Persist imported checksums** in the job database for use in later phases (e.g., verification, copy avoidance).
- **Ensure idempotency and auditability** by logging all imported checksums and their sources.

## Rationale
- **Separation of concerns:** Computing checksums and importing them are distinct operations. This change clarifies the role of the import phase.
- **Performance:** Avoids unnecessary computation during import, leveraging existing trusted checksum data.
- **Auditability:** Makes it clear which checksums were imported versus computed locally.

## Implementation Notes
- Update the CLI and documentation to reflect the new role of `import-checksums`.
- Ensure the database schema can track the source of each checksum (imported vs. computed).
- Provide clear logs and error handling for any mismatches or import issues.

---

*Created: 2025-07-14*
*Author: Agent (GitHub Copilot)*
