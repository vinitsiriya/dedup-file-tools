# Requirements: Move Phase

## Overview
The move phase moves or removes duplicate files to a specified dupes folder as part of the deduplication workflow.

## Requirements
- The CLI must provide a `move` subcommand.
- Must require `--job-dir`, `--job-name`, `--lookup-pool`, and `--dupes-folder` arguments.
- Must move or remove all files identified as duplicates in the database.
- Must update the database with move/removal status for each file.
- Must support multi-threaded operations (default: 4 threads).
- Must log all actions and errors for auditability.
- Must be idempotent and safe to re-run.

## References
- See implementation/move.md and feature/move.md for details.
