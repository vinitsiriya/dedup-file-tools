# Requirements: Verify Phase

## Overview
The verify phase checks that all planned moves/removals were successful and that no duplicates remain in the lookup pool.

## Requirements
- The CLI must provide a `verify` subcommand.
- Must require `--job-dir`, `--job-name`, `--lookup-pool`, and `--dupes-folder` arguments.
- Must verify that all files marked as moved/removed are no longer present in the lookup pool.
- Must check for any remaining duplicates and log discrepancies.
- Must update the database with verification results.
- Must support multi-threaded verification (default: 4 threads).
- Must log all actions and errors for auditability.

## References
- See implementation/verify.md and feature/verify.md for details.
