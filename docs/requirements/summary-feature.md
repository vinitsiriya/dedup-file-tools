# Summary Phase Feature

## Overview
The summary phase provides a final reporting step for the file copy tool. It is designed to give users a clear, auditable summary of what actions were performed, where logs are located, and to generate a CSV report of any files that encountered errors or were not completed.

## Requirements
- The tool must provide a new CLI command: `summary`.
- When invoked, the summary phase must:
  - Print a summary to the console, including:
    - What phases/actions have been performed (as available from logs or state)
    - The location of the main log file
    - A message if all files were copied successfully, or a count of files with errors/pending
  - Generate a CSV file (`summary_report.csv`) in the job directory, listing all files with `copy_status` not equal to `done` (i.e., errors or not completed), including:
    - `uid`
    - `relative_path`
    - `copy_status`
    - `error_message`
- The summary phase must not modify any job state or database records.
- The summary phase must be idempotent and safe to run multiple times.
- The CSV report must be human-readable and suitable for further analysis or audit.

## Rationale
- Users and auditors need a simple, reliable way to see the outcome of a copy job and quickly identify any issues.
- The CSV report enables integration with other tools and workflows for error handling or reporting.

## Acceptance Criteria
- Running the summary command after a job prints a clear summary and generates the correct CSV report.
- If all files are copied successfully, the CSV contains only a header row.
- If there are errors or incomplete files, the CSV lists each with details.
- The feature is covered by automated tests.

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.
