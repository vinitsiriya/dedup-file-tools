# Requirements Summary: dedup_file_tools_dupes_move

This document summarizes all requirements for the deduplication/removal tool, following the documentation agent protocol.

## Functional Requirements
- Modular, phase-based CLI
- SQLite database for job state, file metadata, and audit logs
- Duplicate detection using checksums and metadata
- Move/remove duplicates to dupes folder
- Dry-run, verify, and rollback support
- Logging and idempotency
- Error handling and recovery
- Extensible handler/phase structure

## Non-Functional Requirements
- Robust, maintainable, auditable
- Python 3.8+ compatible
- Cross-platform
- Protocol-compliant documentation

---

See requirements/features/dupes_move.md for feature-specific requirements.
