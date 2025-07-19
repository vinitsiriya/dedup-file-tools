# Requirements: dedup_file_tools_dupes_move

This document defines the requirements for the deduplication/removal workflow, following the documentation agent protocol.

## Functional Requirements
- The tool must provide a modular, phase-based CLI for deduplication/removal workflows.
- The tool must use a SQLite database to track job state, file metadata, and audit logs.
- The tool must detect duplicate files using checksums and metadata.
- The tool must move or remove duplicates to a specified dupes folder.
- The tool must support dry-run, verify, and rollback operations.
- The tool must log all actions for auditability and support idempotent operation.
- The tool must provide clear error handling and recovery mechanisms.
- The tool must be extensible via handler/phase structure.

## Non-Functional Requirements
- The tool must be robust, maintainable, and auditable.
- The tool must be compatible with modern Python versions (3.8+).
- The tool must be cross-platform (Windows, Linux, macOS).
- The tool must have clear, protocol-compliant documentation.

---

See implementation/dupes_move.md and feature/dupes_move.md for related docs.
