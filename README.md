# fs-copy-tool

Safely copy media files (photos, videos) from a source HDD pool to a destination HDD pool, ensuring **no redundant (duplicate) files** at the destination. The tool is robust, resumable, and fully auditable, using an SQLite database for all state and supporting both fixed and removable drives.

---

## Features
- Block-wise (4KB) file copying and SHA-256 checksums
- No file is copied if its checksum already exists in the destination
- All state, logs, and planning files are stored in a dedicated job directory
- Fully resumable and idempotent: safely interrupt and resume at any time
- **Stateful, file-level job setup:**
  - `add-file` — Add a single file to the job state/database
  - `add-source` — Recursively add all files from a directory
  - `list-files` — List all files currently in the job state/database
  - `remove-file` — Remove a file from the job state/database
- CLI commands for all phases: `init`, `analyze`, `import-checksums`, `checksum`, `copy`, `resume`, `status`, `log`, `verify`, `deep-verify`, and more
- Cross-platform: Windows & Linux
- Full test suite for all features and workflows

---

## Quick Start

### 1. Install Requirements
```
pip install -r requirements.txt
```

### 2. Initialize a Job Directory
```
python -m fs_copy_tool.main init --job-dir .copy-task
```

### 3. Add Files or Sources to the Job (Stateful Setup)
# Add a single file:
python -m fs_copy_tool.main add-file --job-dir .copy-task --file <FILE_PATH>
# Add all files from a directory:
python -m fs_copy_tool.main add-source --job-dir .copy-task --src <SRC_ROOT>
# List all files in the job:
python -m fs_copy_tool.main list-files --job-dir .copy-task
# Remove a file from the job:
python -m fs_copy_tool.main remove-file --job-dir .copy-task --file <FILE_PATH>

### 4. Analyze Source and Destination Volumes
```
python -m fs_copy_tool.main analyze --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
```

### 5. Compute Checksums
```
python -m fs_copy_tool.main checksum --job-dir .copy-task --table source_files
python -m fs_copy_tool.main checksum --job-dir .copy-task --table destination_files
```

### 6. Copy Non-Redundant Files
```
python -m fs_copy_tool.main copy --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
```

### 7. Resume, Status, and Logs
```
python -m fs_copy_tool.main resume --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
python -m fs_copy_tool.main status --job-dir .copy-task
python -m fs_copy_tool.main log --job-dir .copy-task
```

### 8. Import Checksums from Old Database (Optional)
```
python -m fs_copy_tool.main import-checksums --job-dir .copy-task --old-db <OLD_DB_PATH> --table source_files
```

---

## CLI Commands
- `init` — Create and initialize a job directory
- `analyze` — Scan source/destination and update the database
- `import-checksums` — Import checksums from an old SQLite database
- `checksum` — Compute missing/stale checksums
- `copy` — Copy only non-duplicate files
- `resume` — Resume incomplete/failed operations
- `status` — Show job progress and statistics
- `log` — Output a log or audit trail
- `add-file` — Add a single file to the job state/database
- `add-source` — Recursively add all files from a directory
- `list-files` — List all files currently in the job state/database
- `remove-file` — Remove a file from the job state/database
- `verify` / `deep-verify` — Shallow/deep verification of copied files

---

## CLI Documentation

See [docs/cli.md](docs/cli.md) for complete CLI command reference, usage examples, and best practices.

---

## Testing
Run all tests (Windows PowerShell):
```
./scripts/test.ps1
```
Or (Linux/macOS):
```
./scripts/test.sh
```

---

## Project Structure
- `fs-copy-tool/` — Main source code
- `tests/` — Automated tests (pytest)
- `agents/` — Agent planning, memory, and reasoning
- `changes/` — Execution logs and persistent state
- `scripts/` — Automation scripts for testing, linting, formatting, and archival
- `Taskfile.yml` — Cross-platform automation tasks

---

## Requirements & Design
See `requirements.md` and `AGENTS.md` for full requirements, design, and agent workflow protocols.

---

## License
MIT License
