# Feature: dedup_file_tools_dupes_move

This document provides a narrative description of the main feature, following the generic documentation protocol.

## Main Feature

The `dedup_file_tools_dupes_move` tool provides a robust, auditable workflow for deduplication and removal of duplicate files. It is designed for maintainability, extensibility, and safe operation in large-scale file management scenarios.

- **Phase-based CLI:** Users can execute deduplication in logical steps (scan, move, verify, rollback).
- **Database-backed:** All operations are tracked for auditability and recovery.
- **Idempotent and safe:** Supports dry-run, verification, and rollback to prevent data loss.
- **Extensible:** New phases and rules can be added as needed.

---

See `requirements/requirements.md` and `features/feature_list.md` for details.
