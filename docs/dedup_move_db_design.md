# Database Design for dedup_file_tools_dupes_move

## Purpose
This document describes the database schema and design principles for the deduplication move tool. The schema is designed for robust, auditable, and resumable duplicate file move operations, supporting full traceability and reporting.

---

## Core Tables

### 1. dedup_files_pool
- **Purpose:** All files scanned, with metadata.
- **Columns:**
  - `uid TEXT`
  - `relative_path TEXT`
  - `size INTEGER`
  - `last_modified INTEGER`
  - `checksum TEXT` (optional, for fast grouping)
  - `scanned_at INTEGER`
- **Primary Key:** `(uid, relative_path)`

### 2. dedup_move_plan
- **Purpose:** The authoritative plan for which files will be moved, where, and why.
- **Columns:**
  - `uid TEXT`
  - `relative_path TEXT`
  - `checksum TEXT`
  - `move_to_uid TEXT`
  - `move_to_rel_path TEXT`
  - `status TEXT` (planned, moved, skipped, error)
  - `error_message TEXT`
  - `planned_at INTEGER`
  - `moved_at INTEGER`
  - `updated_at INTEGER`
  - `is_keeper INTEGER DEFAULT 0` (True if this file is the one kept in place)
- **Primary Key:** `(uid, relative_path)`

### 3. dedup_move_history (optional)
- **Purpose:** Every move attempt, for audit and troubleshooting.
- **Columns:**
  - `uid TEXT`
  - `relative_path TEXT`
  - `attempted_at INTEGER`
  - `action TEXT` (move, skip, error)
  - `result TEXT`
  - `error_message TEXT`

---

## Auxiliary Tables

### 4. dedup_job_meta
- **Purpose:** Store job-level metadata (job name, config, start/end time, user, etc.)
- **Columns:**
  - `job_id TEXT PRIMARY KEY`
  - `job_name TEXT`
  - `created_at INTEGER`
  - `config_json TEXT`
  - `status TEXT`
  - `completed_at INTEGER`

### 5. dedup_group_summary
- **Purpose:** For each duplicate group (by checksum), record summary info.
- **Columns:**
  - `checksum TEXT PRIMARY KEY`
  - `num_files INTEGER`
  - `keeper_uid TEXT`
  - `keeper_rel_path TEXT`
  - `group_status TEXT`

---

## Design Principles
- **Normalization:** Canonical file metadata in `dedup_files_pool`, move plan in `dedup_move_plan`, and history in `dedup_move_history`.
- **Auditability:** Every action (scan, plan, move, error) is timestamped and logged.
- **Resumability:** Status fields and timestamps allow safe resumption and recovery.
- **Performance:** Indexes on `checksum`, `status`, and `move_to_uid, move_to_rel_path` for fast queries.
- **Extensibility:** Easy to add new columns (e.g., for symlink info, permissions, user notes).

---

## Example Schema (SQL)

```sql
CREATE TABLE dedup_files_pool (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    scanned_at INTEGER,
    PRIMARY KEY (uid, relative_path)
);

CREATE TABLE dedup_move_plan (
    uid TEXT,
    relative_path TEXT,
    checksum TEXT,
    move_to_uid TEXT,
    move_to_rel_path TEXT,
    status TEXT,
    error_message TEXT,
    planned_at INTEGER,
    moved_at INTEGER,
    updated_at INTEGER,
    is_keeper INTEGER DEFAULT 0,
    PRIMARY KEY (uid, relative_path)
);

CREATE TABLE dedup_move_history (
    uid TEXT,
    relative_path TEXT,
    attempted_at INTEGER,
    action TEXT,
    result TEXT,
    error_message TEXT
);

CREATE TABLE dedup_job_meta (
    job_id TEXT PRIMARY KEY,
    job_name TEXT,
    created_at INTEGER,
    config_json TEXT,
    status TEXT,
    completed_at INTEGER
);

CREATE TABLE dedup_group_summary (
    checksum TEXT PRIMARY KEY,
    num_files INTEGER,
    keeper_uid TEXT,
    keeper_rel_path TEXT,
    group_status TEXT
);
```

---

## What to Record?
- Every file scanned (with all metadata, for audit and troubleshooting).
- Every planned move (source, destination, status, timestamps, errors).
- Every move attempt (for full traceability).
- Job-level metadata (for reproducibility and audit).
- Group-level summary (for reporting and user review).

---

This design provides full traceability, auditability, and flexibility for future features such as reporting, rollback, or advanced analytics.
