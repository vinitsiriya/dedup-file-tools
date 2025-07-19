# Requirements: Summary Phase

## Overview
The summary phase prints a summary and generates a CSV report of deduplication results for the current job.

## Requirements
- The CLI must provide a `summary` subcommand.
- Must require `--job-dir` and `--job-name` arguments.
- Must read the database and summarize all deduplication actions (scanned, moved, removed, verified, errors).
- Must generate a CSV report with detailed results.
- Must print a human-readable summary to the console.
- Must log all actions and errors for auditability.

## References
- See implementation/summary.md and feature/summary.md for details.
