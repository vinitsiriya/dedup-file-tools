# Non-Redundant Media File Copy Tool — Requirements & Design

## Purpose

Safely copy media files (photos, videos) from a source HDD pool to a destination HDD pool, ensuring **no redundant (duplicate) files** at the destination. The tool must robustly support both fixed and removable drives by tracking volumes using unique IDs (UUID or Serial Number), and be fully resumable and reliable using an SQLite database for all state.

---

## Phases of Operation

### 1. Analysis Phase

* **Objective:**
  Gather and persist metadata for all files in both source and destination pools.

* **Process:**

  * Scan all files on all source and destination volumes.
  * For each file, extract:

    * `uid` (Volume ID, e.g. UUID or Serial Number)
    * `relative_path` (Path relative to the volume root)
    * `size` (File size in bytes)
    * `last_modified` (Epoch time)
  * Insert or update each entry in the respective database table (`source_files`, `destination_files`).
  * If a file is new or its size or modification time has changed, mark `checksum_stale = 1`.

---

### 2. Checksum Sync Phase

* **Objective:**
  Ensure all tracked files have up-to-date content checksums stored in the database.

* **Process:**

  * For every file in both `source_files` and `destination_files` where `checksum IS NULL` or `checksum_stale = 1`:

    * Compute SHA-256 checksum of file content.
    * Update the database record with the checksum and set `checksum_stale = 0`.

---

### 3. Copy Phase

* **Objective:**
  Copy only those files from source to destination whose content (checksum) is not already present in the destination.

* **Process:**

  * For each file in `source_files`:

    * If its checksum exists in any destination file in `destination_files` (with status `'done'`), mark it as `copy_status = 'done'` or equivalent (skip copying).
    * If not present in destination, mark as `copy_status = 'pending'`.
  * For every file marked `copy_status = 'pending'`:

    * Set status to `'in_progress'`.
    * Copy the file from source to destination (preserving relative path as needed).
    * After copying, verify file integrity (size or checksum).
    * On success, mark as `'done'` in both tables and insert or update in `destination_files`.
    * On error, mark as `'error'` and record the error message.
  * **Edge Cases:**
    * Already copied files are always skipped (deduplication).
    * Corrupted files are not fixed by resume/copy logic; errors are reported and must be handled manually.
    * Partial/incomplete copies are detected and retried on resume.

---

### 4. Resume & Retry Logic

* **Objective:**
  Guarantee safe, resumable operation in case of interruption or failure.

* **Process:**

  * At any time, the tool resumes by inspecting the database for any file with `copy_status = 'pending'` or `'error'` and only attempts those files in subsequent runs.
  * Files with `copy_status = 'done'` are never re-copied or re-processed unless their source metadata changes.
  * All resume/copy operations must be idempotent and safe to repeat.

---

### 5. Stateful, File-Level Job Setup

* **Objective:**
  Support incremental, auditable job setup and modification at the file level.

* **Process:**

  * Use CLI commands to manage job state:
    * `add-file` — Add a single file to the job state/database
    * `add-source` — Recursively add all files from a directory
    * `list-files` — List all files currently in the job state/database
    * `remove-file` — Remove a file from the job state/database
  * All job setup and modification must be performed at the file level (directory-level state is not supported).
  * All state changes are persisted in the job directory database and are fully auditable.

---

### 6. Verification & Audit Phases (NEW)

* **Objective:**
  Provide robust verification and auditability of all copy operations.

* **Process:**

  * Support CLI commands for verification:
    * `verify` — Shallow or deep verify: check existence, size, last_modified, or checksums.
    * `deep-verify` — Deep verify: compare checksums between source and destination.
    * `verify-status`, `verify-status-summary`, `verify-status-full` — Show shallow verification results (summary or full history).
    * `deep-verify-status`, `deep-verify-status-summary`, `deep-verify-status-full` — Show deep verification results (summary or full history).
  * Support CLI commands for job status and audit:
    * `status` — Show job progress and statistics.
    * `log` — Show job log or audit trail.
  * All verification and audit results must be persisted and queryable.

---

### 7. Import Checksum Cache Phase

* **Objective:**
  Import externally provided checksums into a dedicated `checksum_cache` table for use as a fallback.

* **Process:**

  * Use the `import-checksums` CLI command to import checksums from an old database or manifest.
  * Imported checksums are stored in the `checksum_cache` table, not in the main tables.
  * All phases (copy, verify, etc.) will use the cache as a fallback if the main table is missing a checksum.

---

## CLI Command Requirements

The following CLI commands and options must be implemented and maintained:

* `init --job-dir <path>`
* `import-checksums --job-dir <path> --old-db <old_db_path> [--table <source_files|destination_files>]`
* `analyze --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]`
* `checksum --job-dir <path> --table <source_files|destination_files> [--threads N] [--no-progress]`
* `copy --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress] [--resume]`
* `resume --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--threads N] [--no-progress]`
* `status --job-dir <path>`
* `log --job-dir <path>`
* `verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...] [--stage <shallow|deep>]`
* `deep-verify --job-dir <path> [--src <src_dir> ...] [--dst <dst_dir> ...]`
* `verify-status --job-dir <path>`
* `deep-verify-status --job-dir <path>`
* `verify-status-summary --job-dir <path>`
* `verify-status-full --job-dir <path>`
* `deep-verify-status-summary --job-dir <path>`
* `deep-verify-status-full --job-dir <path>`
* `add-file --job-dir <path> --file <file_path>`
* `add-source --job-dir <path> --src <src_dir>`
* `list-files --job-dir <path>`
* `remove-file --job-dir <path> --file <file_path>`

All commands must be robust, auditable, and support full state persistence in the job directory.

---

## Database Schema

### `source_files` Table

| Column              | Type                  | Description                                          |
| ------------------- | --------------------- | ---------------------------------------------------- |
| uid                 | TEXT                  | Source volume unique identifier (UUID or Serial No.) |
| relative_path       | TEXT                  | File path relative to volume root                    |
| last_modified       | INTEGER               | Last modified timestamp (epoch)                      |
| size                | INTEGER               | File size in bytes                                   |
| checksum            | TEXT                  | SHA-256 checksum                                     |
| checksum_stale      | INTEGER               | 1 if checksum needs recalculation, 0 if up-to-date   |
| copy_status         | TEXT                  | 'pending', 'in_progress', 'done', 'error'            |
| last_copy_attempt   | INTEGER               | Timestamp of last copy attempt                       |
| error_message       | TEXT                  | Last error message, if any                           |
| PRIMARY KEY         | (uid, relative_path)  |                                                      |

### `destination_files` Table

| Column          | Type                  | Description                                               |
| --------------- | --------------------- | --------------------------------------------------------- |
| uid             | TEXT                  | Destination volume unique identifier (UUID or Serial No.) |
| relative_path   | TEXT                  | File path relative to volume root                         |
| last_modified   | INTEGER               | Last modified timestamp (epoch)                           |
| size            | INTEGER               | File size in bytes                                        |
| checksum        | TEXT                  | SHA-256 checksum                                          |
| checksum_stale  | INTEGER               | 1 if checksum needs recalculation, 0 if up-to-date        |
| copy_status     | TEXT                  | 'done' (other statuses optional for tracking)             |
| error_message   | TEXT                  | Error message if file couldn't be scanned/checked         |
| PRIMARY KEY     | (uid, relative_path)  |                                                           |

### `checksum_cache` Table (NEW)

| Column              | Type                  | Description                                          |
| ------------------- | --------------------- | ---------------------------------------------------- |
| uid                 | TEXT                  | Source volume unique identifier (UUID or Serial No.) |
| relative_path       | TEXT                  | File path relative to volume root                    |
| last_modified       | INTEGER               | Last modified timestamp (epoch)                      |
| size                | INTEGER               | File size in bytes                                   |
| checksum            | TEXT                  | SHA-256 checksum                                     |
| checksum_stale      | INTEGER               | 1 if checksum needs recalculation, 0 if up-to-date   |
| copy_status         | TEXT                  | 'pending', 'in_progress', 'done', 'error'            |
| last_copy_attempt   | INTEGER               | Timestamp of last copy attempt                       |
| error_message       | TEXT                  | Last error message, if any                           |
| PRIMARY KEY         | (uid, relative_path)  |                                                      |

#### Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_source_checksum ON source_files (checksum);
CREATE INDEX IF NOT EXISTS idx_dest_checksum ON destination_files (checksum);
CREATE INDEX IF NOT EXISTS idx_source_status ON source_files (copy_status);
CREATE INDEX IF NOT EXISTS idx_cache_checksum ON checksum_cache (checksum);
```

---

## Checksum Calculation

* All file content hashes are computed using SHA-256, block-wise (4KB per read or as appropriate for your platform).

---

## Volume Identification

* All paths are stored and reconstructed using a `(volume_id, relative_path)` scheme to ensure robustness across changing mount points, drive letters, and removable devices.

---

## Summary

* **All phases and state are persisted in SQLite**—no critical state is held in memory.
* **No file is ever copied if its checksum already exists in the destination.**
* **The tool can be safely interrupted and resumed at any point, with progress, errors, and results tracked and queryable via the database.**
* **All job setup and modification is performed at the file level using stateful CLI commands.**

---

## New Requirements

- Add: Ability to import checksum values for files from an existing (old) SQLite database file, matching on (uid, relative_path, size, last_modified).
- Add: The tool must always store its SQLite database and all job-related files in a dedicated, user-visible job directory (e.g., `.copy-task`). The CLI must support an `init` command to create and initialize this directory, and all subsequent operations must use it for state, logs, and planning files.
- Add: CLI commands for `init`, `analyze`, `import-checksums`, `checksum`, `copy`, `resume`, `status`, `log`/`audit`, and **stateful file-level job setup** (`add-file`, `add-source`, `list-files`, `remove-file`) as described in the accepted proposal.

---

## Test Requirements

- All detailed requirements and protocols for automated, stress, and edge-case testing are maintained in `requirements-test.md`.
- This file (`requirements.md`) will reference `requirements-test.md` for all test-related requirements.

---


