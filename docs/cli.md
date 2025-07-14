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

### analyze
Scan source and destination volumes, gather file metadata, and update the database.
```
analyze --job-dir <path> --src <src_dir> --dst <dst_dir>
```

### checksum
Compute and update checksums for files in the database.
```
checksum --job-dir <path> --table <source_files|destination_files> [--threads N] [--no-progress]
```

### copy
Copy files from source to destination. Skips already completed files and resumes incomplete jobs by default.
```
copy --job-dir <path> --src <src_dir> --dst <dst_dir> [--threads N] [--no-progress] [--resume]
```

### resume
Alias for `copy`. Retries pending/error files and skips completed ones.
```
resume --job-dir <path> --src <src_dir> --dst <dst_dir> [--threads N] [--no-progress]
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
Shallow verify: check existence, size, last_modified.
```
verify --job-dir <path> --src <src_dir> --dst <dst_dir>
```

### deep-verify
Deep verify: compare checksums between source and destination.
```
deep-verify --job-dir <path> --src <src_dir> --dst <dst_dir>
```

### verify-status, verify-status-summary, verify-status-full
Show shallow verification results (summary or full history).
```
verify-status --job-dir <path>
verify-status-summary --job-dir <path>
verify-status-full --job-dir <path>
```

### deep-verify-status, deep-verify-status-summary, deep-verify-status-full
Show deep verification results (summary or full history).
```
deep-verify-status --job-dir <path>
deep-verify-status-summary --job-dir <path>
deep-verify-status-full --job-dir <path>
```

### import-checksums
Import checksums from an old SQLite database into the checksum cache table. These imported checksums are used as a fallback when the main tables are missing a checksum.
```
import-checksums --job-dir <path> --old-db <old_db_path> --table <source_files|destination_files>
```
- Imported checksums are stored in the `checksum_cache` table, not in `source_files` or `destination_files`.
- All phases (copy, verify, etc.) will use the cache as a fallback if the main table is missing a checksum.

## Best Practices
- Always use a dedicated job directory for each migration session.
- Use the `status` and `log` commands to monitor progress and troubleshoot issues.
- Use the `resume` or `copy` command to safely continue interrupted jobs.
- Run `verify` and `deep-verify` after copying to ensure data integrity.
- For manual and automated tests, use the `.temp` directory as described in the documentation.

## Example Workflow
```
.venv\Scripts\python.exe fs_copy_tool/main.py init --job-dir .temp/job
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
