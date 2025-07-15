# Non-Redundant Media File Copy Tool — Requirements & Design

## Purpose

Safely copy media files (photos, videos) from a source HDD pool to a destination HDD pool, ensuring **no redundant (duplicate) files** at the destination. The tool must robustly support both fixed and removable drives by tracking volumes using unique IDs (UUID or Serial Number), and be fully resumable and reliable using an SQLite database for all state.

---

## Phases of Operation

### 1. Analysis Phase

* **Objective:**
  Gather and persist metadata for all files in both source and destination pools.

* **Process:**

  * If a file is new or its size or modification time has changed, mark `checksum_stale = 1`.

---

### 2. Checksum Sync Phase

* **Objective:**
  Ensure all tracked files have up-to-date content checksums stored in the database.

---

### 3. Copy Phase

* **Objective:**
  Copy only those files from source to destination whose content (checksum) is not already present in the destination.

---

### 4. Resume & Retry Logic

* **Objective:**
  Guarantee safe, resumable operation in case of interruption or failure.

* **Process:**

  * All resume/copy operations must be idempotent and safe to repeat.

---

### 5. Stateful, File-Level Job Setup

* **Objective:**
  Support incremental, auditable job setup and modification at the file level.

* **Process:**

  * All state changes are persisted in the job directory database and are fully auditable.

---

### 6. Verification & Audit Phases

* **Objective:**
  Provide robust verification and auditability of all copy operations.

* **Process:**

  * All verification and audit results must be persisted and queryable.

---

### 7. Import Checksum Cache Phase (2025-07-15)

* **Objective:**
  Import externally provided checksums into a dedicated `checksum_cache` table for use as a fallback.

* **Process:**

  * Only import from the `checksum_cache` table of another compatible database using `import-checksums --job-dir <path> --other-db <other_db_path>`.
  * All phases (copy, verify, etc.) will use the cache as a fallback if the main table is missing a checksum.

---

## CLI Command Requirements

The following CLI commands and options must be implemented and maintained:

* `init --job-dir <path>`
* `import-checksums --job-dir <path> --other-db <other_db_path>`
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
| relative_path   | TEXT                  | File path relative to volume root                        |
| last_modified   | INTEGER               | Last modified timestamp (epoch)                          |
| size            | INTEGER               | File size in bytes                                       |
| checksum        | TEXT                  | SHA-256 checksum                                         |
| copy_status     | TEXT                  | 'pending', 'in_progress', 'done', 'error'                |
| error_message   | TEXT                  | Last error message, if any                               |
| PRIMARY KEY     | (uid, relative_path)  |                                                         |

### `checksum_cache` Table

| Column          | Type                  | Description                                               |
| --------------- | --------------------- | --------------------------------------------------------- |
| uid             | TEXT                  | Volume unique identifier                                 |
| relative_path   | TEXT                  | File path relative to volume root                        |
| size            | INTEGER               | File size in bytes                                       |
| last_modified   | INTEGER               | Last modified timestamp (epoch)                          |
| checksum        | TEXT                  | SHA-256 checksum                                         |
| imported_at     | INTEGER               | Import timestamp                                         |
| last_validated  | INTEGER               | Last validation timestamp                                |
| is_valid        | INTEGER               | 1 if valid, 0 if stale                                   |
| PRIMARY KEY     | (uid, relative_path)  |                                                         |

(Other tables: `verification_shallow_results`, `verification_deep_results` are also present for job state and verification.)

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


