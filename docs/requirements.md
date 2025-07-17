## One-Shot Command (2025-07)

- The tool MUST provide a `one-shot` CLI command to run the entire workflow (init, import, add-source, analyze, checksum, copy, verify, summary) in a single step.
- The command MUST accept all required and optional arguments for the full workflow.
- The workflow MUST stop immediately and print an error if any step fails.
- The command MUST print "Done" on success.
- See `requirements/one-shot.md` for full details.
# Non-Redundant Media File Copy Tool — Requirements & Design


## Purpose

Safely copy media files (photos, videos) from a source HDD pool to a destination HDD pool, ensuring **no redundant (duplicate) files** at the destination. The tool robustly supports both fixed and removable drives by tracking volumes using unique IDs (UUID or Serial Number), and is fully resumable and reliable using an SQLite database for all state.

---

## Architecture Update (2025-07)

- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.
- All documentation, requirements, and test protocols must use the new DB naming and CLI conventions.
- Legacy `copytool.db` is no longer supported.

---

## Phases of Operation

### 1. Analysis Phase

* **Objective:**
  Gather and persist metadata for all files in both source and destination pools using `UidPath` abstraction.

* **Process:**

  * If a file is new or its size or modification time has changed, mark `checksum_stale = 1`.
  * Handle missing UIDs and non-directory roots gracefully.

---


### `source_files` Table

| Column            | Type      | Description                                                      |
|-------------------|-----------|------------------------------------------------------------------|
| uid               | TEXT      | Source volume unique identifier (UUID or Serial No.)             |
| relative_path     | TEXT      | File path relative to volume root                                |
| last_modified     | INTEGER   | Last modified timestamp (epoch)                                  |
| size              | INTEGER   | File size in bytes                                               |
| copy_status       | TEXT      | 'pending', 'in_progress', 'done', 'error'                        |
| last_copy_attempt | INTEGER   | Timestamp of last copy attempt                                   |
| error_message     | TEXT      | Last error message, if any                                       |
| PRIMARY KEY       | (uid, relative_path) |                                                          |

### `destination_files` Table

| Column          | Type      | Description                                                      |
|-----------------|-----------|------------------------------------------------------------------|
| uid             | TEXT      | Destination volume unique identifier (UUID or Serial No.)         |
| relative_path   | TEXT      | File path relative to volume root                                |
| last_modified   | INTEGER   | Last modified timestamp (epoch)                                  |
| size            | INTEGER   | File size in bytes                                               |
| copy_status     | TEXT      | 'pending', 'in_progress', 'done', 'error'                        |
| error_message   | TEXT      | Last error message, if any                                       |
| PRIMARY KEY     | (uid, relative_path) |                                                          |

### `checksum_cache` Table

| Column          | Type      | Description                                                      |
|-----------------|-----------|------------------------------------------------------------------|
| uid             | TEXT      | Volume unique identifier                                         |
| relative_path   | TEXT      | File path relative to volume root                                |
| size            | INTEGER   | File size in bytes                                               |
| last_modified   | INTEGER   | Last modified timestamp (epoch)                                  |
| checksum        | TEXT      | SHA-256 checksum                                                 |
| imported_at     | INTEGER   | Import timestamp                                                 |
| last_validated  | INTEGER   | Last validation timestamp                                        |
| is_valid        | INTEGER   | 1=valid, 0=stale                                                 |
| PRIMARY KEY     | (uid, relative_path) |                                                          |

### `destination_pool_files` Table

| Column          | Type      | Description                                                      |
|-----------------|-----------|------------------------------------------------------------------|
| uid             | TEXT      | Volume unique identifier                                         |
| relative_path   | TEXT      | File path relative to volume root                                |
| size            | INTEGER   | File size in bytes                                               |
| last_modified   | INTEGER   | Last modified timestamp (epoch)                                  |
| last_seen       | INTEGER   | Last time this file was seen in the pool (epoch)                 |
| PRIMARY KEY     | (uid, relative_path) |                                                          |

### `verification_shallow_results` Table

| Column                  | Type      | Description                                                  |
|-------------------------|-----------|--------------------------------------------------------------|
| uid                     | TEXT      | Volume unique identifier                                     |
| relative_path           | TEXT      | File path relative to volume root                            |
| exists                  | INTEGER   | 1 if file exists, 0 otherwise                                |
| size_matched            | INTEGER   | 1 if size matches, 0 otherwise                               |
| last_modified_matched   | INTEGER   | 1 if last_modified matches, 0 otherwise                      |
| expected_size           | INTEGER   | Expected file size                                           |
| actual_size             | INTEGER   | Actual file size                                             |
| expected_last_modified  | INTEGER   | Expected last modified timestamp                             |
| actual_last_modified    | INTEGER   | Actual last modified timestamp                               |
| verify_status           | TEXT      | Verification status                                          |
| verify_error            | TEXT      | Verification error message                                   |
| timestamp               | INTEGER   | Verification timestamp (epoch)                               |
| PRIMARY KEY             | (uid, relative_path, timestamp) |                              |

### `verification_deep_results` Table

| Column            | Type      | Description                                                  |
|-------------------|-----------|--------------------------------------------------------------|
| uid               | TEXT      | Volume unique identifier                                     |
| relative_path     | TEXT      | File path relative to volume root                            |
| checksum_matched  | INTEGER   | 1 if checksum matches, 0 otherwise                           |
| expected_checksum | TEXT      | Expected checksum                                            |
| src_checksum      | TEXT      | Source file checksum                                         |
| dst_checksum      | TEXT      | Destination file checksum                                    |
| verify_status     | TEXT      | Verification status                                          |
| verify_error      | TEXT      | Verification error message                                   |
| timestamp         | INTEGER   | Verification timestamp (epoch)                               |
| PRIMARY KEY       | (uid, relative_path, timestamp) |                                  |

(All indexes and schema details are defined in `db.py` and are kept in sync with this documentation.)
  Provide robust verification and auditability of all copy operations.

* **Process:**

  * Shallow verify: checks existence, size, last_modified.
  * Deep verify: compares checksums using `ChecksumCache` as the only source of truth.
  * All verification and audit results are persisted and queryable.

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


### `destination_pool_files` Table

| Column          | Type      | Description                                               |
| --------------  | --------- | --------------------------------------------------------- |
| uid             | TEXT      | Volume unique identifier                                 |
| relative_path   | TEXT      | File path relative to volume root                        |
| size            | INTEGER   | File size in bytes                                       |
| last_modified   | INTEGER   | Last modified timestamp (epoch)                          |
| last_seen       | INTEGER   | Last time this file was seen in the pool (epoch)         |
| PRIMARY KEY     | (uid, relative_path) |                                             |

*This table is updated by scanning the destination root(s) and is used for global deduplication. It is always validated and updated before the copy phase.*

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

## System-Independent Path Abstraction

* All file operations use `UidPath` for robust, portable referencing.
* UID is the volume serial (Windows) or UUID (Linux); relative path is always relative to the mount point.

---

## Checksum Calculation

* All file content hashes are computed using SHA-256, block-wise (4KB per read or as appropriate for your platform).

---

## Volume Identification

* All paths are stored and reconstructed using a `(volume_id, relative_path)` scheme to ensure robustness across changing mount points, drive letters, and removable devices.

---

## Auditability & Error Handling

* All phases are auditable, resumable, and provide clear error reporting.
* All state and logs are persisted in the job directory database.

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


