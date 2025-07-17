# fs-copy-tool CLI Documentation

## Overview
`fs-copy-tool` is a robust, resumable, and auditable file copy utility designed for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state and supports full workflow automation, verification, and resume.

## Usage

All commands are run via the project's virtual environment Python:

```
.venv\Scripts\python.exe fs_copy_tool/main.py <command> [options]
```

## Commands


### Main Commands & Options
init --job-dir <path>
Initialize a new job directory (creates database and state files).

import-checksums --job-dir <path> --other-db <other_db_path>
Import checksums from another compatible job database.

analyze --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]
Analyze source and/or destination volumes to gather file metadata.

checksum --job-dir <path> --table <source_files|destination_files> [--threads N] [--no-progress]
Compute or update checksums for files in the specified table.

copy --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress] [--resume]
Copy files from source to destination, skipping duplicates and resuming incomplete jobs.
--resume is always enabled by default and can be omitted.
Before copying, all destination pool checksums are updated and validated with a progress bar to ensure deduplication is accurate and up to date.

resume --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress]
Resume interrupted or failed copy operations.

status --job-dir <path>
Show job progress and statistics.

log --job-dir <path>
Show job log or audit trail.

verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--stage <shallow|deep>]
Verify copied files. Use --stage shallow for basic attribute checks, or --stage deep for checksum comparison.

deep-verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]
Perform deep verification (checksum comparison) between source and destination.

verify-status --job-dir <path>
Show a summary of the latest shallow verification results for each file.

deep-verify-status --job-dir <path>
Show a summary of the latest deep verification results for each file.

verify-status-summary --job-dir <path>
Show a short summary of shallow verification results.

verify-status-full --job-dir <path>
Show all shallow verification results (full history).

deep-verify-status-summary --job-dir <path>
Show a short summary of deep verification results.

deep-verify-status-full --job-dir <path>
Show all deep verification results (full history).

add-file --job-dir <path> --file <file_path>
Add a single file to the job database.

add-source --job-dir <path> --src <src_dir>
Recursively add all files from a directory to the job database.
(Uses batching and multithreading for fast file addition; progress bar is shown for large directories.)

add-to-destination-index-pool --job-dir <path> --dst <dst_dir>
Scan and add/update all files in the destination pool index.

list-files --job-dir <path>
List all files currently in the job database.

remove-file --job-dir <path> --file <file_path>
Remove a file from the job database.

summary --job-dir <path>
Print a summary of the job, including what has happened, where the logs are, and generate a CSV report (summary_report.csv) of all files with errors or not done.

Notes:

All commands are run via Python (use the virtual environment if available):
Or, if installed as a package:
For verification, always use --stage shallow or --stage deep (not --phase).
The add-source command is optimized for large datasets using batching and multithreading, and will show a progress bar for visibility.
All operations are resumable, auditable, and robust against interruption.

## Best Practices
- Always use a dedicated job directory for each migration session.
- Use the `status` and `log` commands to monitor progress and troubleshoot issues.
- Use the `resume` or `copy` command to safely continue interrupted jobs.
- Run `verify` and `deep-verify` after copying to ensure data integrity.
- For manual and automated tests, use a dedicated temp directory as described in the documentation.

## Example Workflow
```
.venv\Scripts\python.exe fs_copy_tool/main.py init --job-dir .temp/job
.venv\Scripts\python.exe fs_copy_tool/main.py add-source --job-dir .temp/job --src .temp/src
.venv\Scripts\python.exe fs_copy_tool/main.py list-files --job-dir .temp/job
.venv\Scripts\python.exe fs_copy_tool/main.py analyze --job-dir .temp/job --src .temp/src --dst .temp/dst
.venv\Scripts\python.exe fs_copy_tool/main.py checksum --job-dir .temp/job --table source_files
.venv\Scripts\python.exe fs_copy_tool/main.py checksum --job-dir .temp/job --table destination_files
.venv\Scripts\python.exe fs_copy_tool/main.py copy --job-dir .temp/job --src .temp/src --dst .temp/dst
.venv\Scripts\python.exe fs_copy_tool/main.py status --job-dir .temp/job
.venv\Scripts\python.exe fs_copy_tool/main.py verify --job-dir .temp/job --src .temp/src --dst .temp/dst
.venv\Scripts\python.exe fs_copy_tool/main.py deep-verify --job-dir .temp/job --src .temp/src --dst .temp/dst
.venv\Scripts\python.exe fs_copy_tool/main.py import-checksums --job-dir .temp/job --job-name <job-name> --other-db .temp/other_job/checksum-cache.db
 .venv\Scripts\python.exe fs_copy_tool/main.py summary --job-dir .temp/job
```

---

For more details, see the project README and documentation files.
