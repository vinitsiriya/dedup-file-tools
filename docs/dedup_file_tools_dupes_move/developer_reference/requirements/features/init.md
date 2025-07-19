# Requirements: Init Phase

## Overview
The init phase sets up a new deduplication job, creating the job directory and initializing the SQLite database.

## Requirements
- The CLI must provide an `init` subcommand.
- Must require `--job-dir` and `--job-name` arguments.
- Must create the job directory if it does not exist.
- Must create a new SQLite database for job state and metadata.
- Must fail with a clear error if the job already exists.
- Must be idempotent if run multiple times with the same arguments.

## References
- See implementation/init.md and feature/init.md for details.
