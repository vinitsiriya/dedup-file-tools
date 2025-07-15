# fs-copy-tool CLI Documentation

## Overview
`fs-copy-tool` is a robust, resumable, and auditable file copy utility designed for safe, non-redundant media migration between storage pools. It uses an SQLite database to track all state and supports full workflow automation, verification, and resume.

## Usage

All commands are run via the project's virtual environment Python:

```
.venv\Scripts\python.exe fs_copy_tool/main.py <command> [options]
```

## Commands

### init
Initialize a new job directory and database.
```
init --job-dir <path>
```

### import-checksums
Import checksums from an old SQLite database into the checksum cache table. These imported checksums are used as a fallback when the main tables are missing a checksum.
```
import-checksums --job-dir <path> --old-db <old_db_path> [--table <source_files|destination_files>]
```
- `--table` defaults to `source_files` if not specified.

### analyze
Scan source and/or destination volumes, gather file metadata, and update the database.
```
analyze --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]
```

### checksum
Compute and update checksums for files in the database.
```
checksum --job-dir <path> --table <source_files|destination_files> [--threads N] [--no-progress]
```
- `--threads` defaults to 4.
- `--no-progress` disables the progress bar.

### copy
Copy files from source to destination. Skips already completed files and resumes incomplete jobs by default.
```
copy --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress] [--resume]
```
- `--resume` is always enabled by default and can be omitted.

### resume
Alias for `copy`. Retries pending/error files and skips completed ones.
```
resume --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress]
```

### status
Show job progress and statistics.
```
status --job-dir <path>
```

### log
Show job log or audit trail.
```
log --job-dir <path>
```

### verify
Shallow or deep verify: check existence, size, last_modified, or checksums.
```
verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--stage <shallow|deep>]
```
- `--stage` defaults to `shallow`.

### deep-verify
Deep verify: compare checksums between source and destination.
```
deep-verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]
```

### verify-status
Show a summary of the latest shallow verification results for each file.
```
verify-status --job-dir <path>
```

### deep-verify-status
Show a summary of the latest deep verification results for each file.
```
deep-verify-status --job-dir <path>
```

### verify-status-summary
Show a short summary of the latest shallow verification results for each file.
```
verify-status-summary --job-dir <path>
```

### verify-status-full
Show all shallow verification results (full history).
```
verify-status-full --job-dir <path>
```

### deep-verify-status-summary
Show a short summary of the latest deep verification results for each file.
```
deep-verify-status-summary --job-dir <path>
```

### deep-verify-status-full
Show all deep verification results (full history).
```
deep-verify-status-full --job-dir <path>
```

### add-file
Add a single file to the job state/database.
```
add-file --job-dir <path> --file <file_path>
```

### add-source
Recursively add all files from a directory to the job state/database.
```
add-source --job-dir <path> --src <src_dir>
```

### list-files
List all files currently in the job state/database.
```
list-files --job-dir <path>
```

### remove-file
Remove a file from the job state/database.
```
remove-file --job-dir <path> --file <file_path>
```

## Best Practices
- Always use a dedicated job directory for each migration session.
- Use the `status` and `log` commands to monitor progress and troubleshoot issues.
- Use the `resume` or `copy` command to safely continue interrupted jobs.
- Run `verify` and `deep-verify` after copying to ensure data integrity.
- For manual and automated tests, use the `.temp` directory as described in the documentation.

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
```

---

For more details, see the project README and documentation files.
