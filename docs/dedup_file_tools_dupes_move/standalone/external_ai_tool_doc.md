



# External AI Tool & Agent Integration: dedup_file_tools_dupes_move

## Table of Contents
1. [Overview](#overview)
2. [Protocol Compliance](#protocol-compliance)
3. [CLI Automation & YAML Config Usage](#cli-automation--yaml-config-usage)
4. [Log & CSV Parsing, Audit Trails](#log--csv-parsing-audit-trails)
5. [Example Agent Workflow](#example-agent-workflow)
6. [Error Handling, Reproducibility, and Protocol Compliance](#error-handling-reproducibility-and-protocol-compliance)
7. [Full CLI Reference](#full-cli-reference)
8. [References](#references)

---

## Overview
This document provides a protocol-driven, phase-by-phase reference for integrating external AI tools and agents with the deduplication/removal tool. It is intended for:
- Developers building automation or orchestration around the deduplication CLI
- AI agents responsible for documentation, testing, or workflow automation
- Anyone needing to ensure auditable, reproducible, and protocol-compliant integration

Integration points include:
- CLI automation (all phases)
- YAML config management
- Log and CSV parsing for validation and reporting
- Documentation and audit trail updates

## Protocol Compliance
- All agent/AI tool actions must strictly follow the documentation agent protocol (`docs/agent/documentation-agent-protocol.md`).
- Agents must update documentation in the correct order and directory structure, and note any files that did not require changes.
- All CLI automation, test runs, and documentation updates must be auditable and reproducible.

---

## CLI Automation & YAML Config Usage
- Agents/AI tools can automate all CLI phases (`init`, `analyze`, `preview-summary`, `move`, `verify`, `summary`, `one-shot`) by invoking the Python CLI with the correct arguments.
- YAML config files can be used for reproducible CLI runs. Command-line arguments always override config values (see `main.py`, `load_yaml_config`, and `merge_config_with_args`).
- Agents must always specify the correct `--job-dir` and `--job-name` to ensure all state, logs, and outputs are auditable and reproducible.
- All agent actions (documentation updates, audits, CLI invocations) must be logged in `agent-context.md` and `dev-notes.md` in `agents/workflow/implementation-strategies/dedup_file_tools_dupes_move_doc_update/`.

## Log & CSV Parsing, Audit Trails
- Agents/AI tools must parse logs and summary CSVs in the job directory for automated validation, reporting, and error detection.
- All CLI actions, results, and errors are logged in the job directory and must be referenced in agent audit trails.
- Every agent/AI tool action must be traceable in `agent-context.md` and `dev-notes.md`.



## Error Handling, Reproducibility, and Protocol Compliance
- All errors, exceptions, and failed CLI runs must be logged and reported in agent audit trails.
- Agents/AI tools must ensure all actions are reproducible by using YAML configs and explicit CLI arguments.
- All documentation and automation must comply with the project’s documentation agent protocol and workflow rules.

---

## Full CLI Reference

# CLI Reference: dedup_file_tools_dupes_move

This document provides a precise, phase-by-phase reference for the deduplication/removal tool CLI, matching the code in main.py and all handler/phase logic exactly.

## Overview
The deduplication/removal tool is a modular, phase-based CLI for scanning, grouping, and moving/removing duplicate files. Each command (phase) is implemented as a handler, with all state and metadata tracked in a job-specific SQLite database. The tool is robust, auditable, and supports YAML config files for reproducible workflows.

**Global Behavior:**
- All commands require a job directory (`--job-dir`) and job name (`--job-name`), which determine the database location.
- All file operations, status, and logs are tracked in the job directory.
- YAML config files can be loaded with `--config`; command-line arguments always override config values.
- Logging is controlled by `--log-level` and logs are written to the job directory.
- If a required argument is missing, the CLI prints help and exits.
- If a file is missing or an operation fails, an error is logged and the workflow stops (for one-shot) or continues as appropriate for the phase.

---

## Usage

```
dedup-file-move-dupes <command> [OPTIONS]
```

## Global Options
- `--log-level LEVEL` (default: INFO): Set logging verbosity (info, debug, etc.)
- `--config FILE`: Load options from a YAML config file (command-line args override config)
- `--help`: Show help for any phase or the main CLI

## Commands and Arguments

### `import-checksums`
**Purpose:** Import checksums from another compatible database's `checksum_cache` table into this job's checksum cache. Useful for reusing or merging checksum data across jobs or runs.

**Arguments:**
- `--job-dir PATH` (required): Directory to store job state and database
- `--job-name NAME` (required): Name for this deduplication job
- `--other-db PATH` (required): Path to another compatible SQLite database (must have a `checksum_cache` table)
- `--checksum-db PATH` (optional): Custom checksum DB path (default: `<job-dir>/checksum-cache.db`)

**Internal Logic:**
- Validates that the other database has a `checksum_cache` table
- Reads all rows from the other database's `checksum_cache`
- Efficiently imports all rows into the current job's checksum cache using batched inserts
- Progress is shown with a progress bar
- Logs the number of imported rows and the final count

**Outputs/Side Effects:**
- Updates the job's checksum cache database with imported checksums
- Logs all actions and errors

**Error Handling:**
- Fails with a clear error if the other database is missing or does not have a `checksum_cache` table
- Fails if the import cannot be completed (e.g., DB error)

---

### `init`
**Purpose:** Initialize a new deduplication job. Creates the job directory (if needed) and initializes the SQLite database for all future phases.

**Arguments:**
- `--job-dir PATH` (required): Directory to store job state, logs, and database
- `--job-name NAME` (required): Name for this deduplication job (database will be `<job-name>.db`)

**Internal Logic:**
- Creates the job directory if it does not exist
- Creates a new SQLite database for job state and metadata
- Attaches a checksum cache database for efficient duplicate detection
- Logs all actions to the job directory

**Outputs/Side Effects:**
- Creates `<job-dir>/<job-name>.db` and checksum cache DB
- Logs initialization in the job directory

**Error Handling:**
- Fails with a clear error if the job already exists or DB cannot be created
- Idempotent: running multiple times with the same arguments is safe


### `analyze`
**Purpose:** Scan the lookup pool, compute checksums, persist all file metadata, group by checksum, and queue all but one file per group in the move plan.

**Arguments:**
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--lookup-pool PATH` (required): Path to folder to scan for duplicates
- `--threads N` (default: 4): Number of threads for parallel checksumming

**Internal Logic:**
- Recursively scans all files in the lookup pool
- Computes checksums for each file (using a cache for efficiency)
- Persists file metadata to the database (`dedup_files_pool`)
- Groups files by checksum and queues all but one per group in `dedup_move_plan`
- Logs progress and errors

**Outputs/Side Effects:**
- Updates the job database with file metadata and move plan
- Logs analysis results and progress

**Error Handling:**
- Logs and skips files that cannot be read or checksummed
- Fails if the database cannot be updated

### `preview-summary`
**Purpose:** Preview planned duplicate groups and moves before executing the move phase.

**Arguments:**
- `--job-dir PATH` (required)
- `--job-name NAME` (required)

**Internal Logic:**
- Reads the job database and summarizes planned duplicate groups and move actions
- Prints a preview to the console

**Outputs/Side Effects:**
- Console output showing planned duplicate groups and moves
- No changes to the database or files

**Error Handling:**
- Fails with a clear error if the database is missing or corrupt

### `move`
**Purpose:** Move or remove duplicate files as planned, updating the database and logging all actions.

**Arguments:**
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--dupes-folder PATH` (optional): Folder to move duplicates into (removal folder). If not provided, it is loaded from job metadata (set during the first move phase).
- `--threads N` (default: 4): Number of threads for move phase

**Internal Logic:**
- Reads the move plan from the database
- For each planned duplicate, moves the file to the removal folder (using fast-move or copy-delete as needed)
- Updates the database with move status and logs each action
- Handles cross-device moves and logs the move type
- If `dupes-folder` is not provided, loads it from job metadata (set during the first move phase)

**Outputs/Side Effects:**
- Files are moved or removed as planned
- Database is updated with move status and history
- Logs all actions and errors

**Error Handling:**
- Logs and skips files that cannot be moved
- Fails if the database cannot be updated

### `verify`
**Purpose:** Verify that all planned moves/removals were successful and that no duplicates remain in the lookup pool.

**Arguments:**
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--threads N` (default: 4): Number of threads for verification

**Internal Logic:**
- Reads the move plan and verifies that all files marked as moved/removed are no longer present in the lookup pool
- Checks file size and optionally verifies checksums
- Updates the database with verification results and logs discrepancies
- Loads `dupes-folder` from job metadata (set during the move phase)

**Outputs/Side Effects:**
- Database is updated with verification results
- Logs all actions and errors
- Console output of verification summary

**Error Handling:**
- Logs and reports missing files or checksum mismatches
- Fails if the database cannot be updated

### `summary`
**Purpose:** Print a summary and generate a CSV report of deduplication results for the current job.

**Arguments:**
- `--job-dir PATH` (required)
- `--job-name NAME` (required)

**Internal Logic:**
- Reads the job database and summarizes all deduplication actions (scanned, moved, removed, verified, errors)
- Generates a CSV report with detailed results in the job directory
- Prints a human-readable summary to the console

**Outputs/Side Effects:**
- CSV report written to `<job-dir>/dedup_move_summary.csv`
- Console output of summary and status counts
- Logs all actions

**Error Handling:**
- Fails with a clear error if the database is missing or corrupt

### `one-shot`
**Purpose:** Run the full deduplication workflow (init, analyze, preview-summary, move, verify, summary) in one command for maximum automation and reproducibility.

**Arguments:**
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--lookup-pool PATH` (required)
- `--dupes-folder PATH` (required)
- `--threads N` (default: 4): Number of threads for all phases

**Internal Logic:**
- Runs all phases in order: init, analyze, preview-summary, move, verify, summary
- Each phase is called with the same arguments as if run individually
- Logs all actions and errors

**Outputs/Side Effects:**
- All job state, logs, and reports are created as in the individual phases
- Console output and CSV summary as in the summary phase

**Error Handling:**
- If any phase fails, the workflow stops immediately and prints/logs an error
- On success, prints/logs "One-shot workflow complete."

## YAML Config Support
All commands support loading options from a YAML config file using `--config FILE`. Command-line arguments always override config values.

## Example Usage

```
dedup-file-move-dupes one-shot --job-dir ./jobs --job-name myjob --lookup-pool ./data --dupes-folder ./dupes
dedup-file-move-dupes analyze --job-dir ./jobs --job-name myjob --lookup-pool ./data --threads 8
dedup-file-move-dupes preview-summary --job-dir ./jobs --job-name myjob
```
Or, using a YAML config file:
```
dedup-file-move-dupes one-shot --config config.yaml
```

## Error Handling
- If any required argument is missing, the CLI prints help and exits.
- If a file is missing or an operation fails, an error is logged and the workflow stops (for one-shot) or continues as appropriate for the phase.

## References
- See `requirements/features/<command>.md`, `implementation/<command>.md`, and `feature/<command>.md` for detailed requirements and implementation notes for each command.

---

## References
- `main.py` — CLI entry point and argument parsing logic
- `handlers.py` — Handler functions for each CLI phase
- `phases/` — Implementation of each deduplication phase (analyze, move, verify, summary, etc.)
- `utils/config_loader.py` — YAML config loading and argument merging
- `docs/agent/documentation-agent-protocol.md` — Documentation agent protocol (required for all agent/AI tool actions)
- `agents/workflow/implementation-strategies/dedup_file_tools_dupes_move_doc_update/agent-context.md` — Agent context and plan
- `agents/workflow/implementation-strategies/dedup_file_tools_dupes_move_doc_update/dev-notes.md` — Agent audit trail and update log
- `docs/agent/documentation-agent-protocol.md` for protocol reference
