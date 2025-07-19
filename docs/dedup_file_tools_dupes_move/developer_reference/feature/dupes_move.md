# Feature: dedup_file_tools_dupes_move

This document provides a user- and agent-facing description of the deduplication/removal workflow, following the documentation agent protocol.

## Main Feature
- Robust, auditable deduplication/removal workflow for large file sets
- Phase-based CLI: init, analyze, move, verify, summary, one-shot
- Database-backed for traceability and recovery
- Idempotent, safe operations (dry-run, verify, rollback)
- Extensible handler/phase structure

## Usage Example
```
python -m dedup_file_tools_dupes_move.main one-shot --job-dir ./jobs --job-name myjob --lookup-pool ./data --dupes-folder ./dupes
```

---

See requirements/features/dupes_move.md and implementation/dupes_move.md for details.
