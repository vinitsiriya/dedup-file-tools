# fs-copy-tool

Safely copy media files (photos, videos) from a source HDD pool to a destination HDD pool, ensuring **no redundant (duplicate) files** at the destination. The tool is robust, resumable, and fully auditable, using an SQLite database for all state and supporting both fixed and removable drives.

---

## Features
- Block-wise (4KB) file copying and SHA-256 checksums
- No file is copied if its checksum already exists in the destination
- All state, logs, and planning files are stored in a dedicated job directory
- Fully resumable and idempotent: safely interrupt and resume at any time
- CLI commands for all phases: `init`, `analyze`, `import-checksums`, `checksum`, `copy`, `resume`, `status`, `log`
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

### 3. Analyze Source and Destination Volumes
```
python -m fs_copy_tool.main analyze --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
```

### 4. Compute Checksums
```
python -m fs_copy_tool.main checksum --job-dir .copy-task --table source_files
python -m fs_copy_tool.main checksum --job-dir .copy-task --table destination_files
```

### 5. Copy Non-Redundant Files
```
python -m fs_copy_tool.main copy --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
```

### 6. Resume, Status, and Logs
```
python -m fs_copy_tool.main resume --job-dir .copy-task --src <SRC_ROOT> --dst <DST_ROOT>
python -m fs_copy_tool.main status --job-dir .copy-task
python -m fs_copy_tool.main log --job-dir .copy-task
```

### 7. Import Checksums from Old Database (Optional)
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
