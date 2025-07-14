# main.md - Requirements Documentation for main.py

## Purpose
This module is the main orchestration script for the Non-Redundant Media File Copy Tool. It provides the CLI, job management, and command dispatch for all phases of the workflow.

## Key Requirements

### 1. Job Initialization
- The tool must allow users to initialize a new job directory with a dedicated SQLite database for tracking file copy state.
- The job directory must be created if it does not exist.
- The database must be initialized with the required schema.

### 2. CLI Argument Parsing
- The tool must provide a command-line interface with subcommands for each workflow phase (init, analyze, checksum, copy, verify, etc.).
- Argument parsing must be separated from command dispatch to enable unit testing.
- Each subcommand must have a dedicated handler function.

### 3. Source and File Registration
- The tool must allow users to add individual files or recursively add all files from a source directory to the job database.
- All files must be registered using a system-independent UID and a relative path, as provided by UidPath.
- The database must be updated or created as needed for each file.

### 4. Phase Dispatch
- The tool must dispatch to the correct phase handler (analyze, checksum, copy, verify, etc.) based on the CLI command.
- Each handler must receive parsed arguments and perform its phase logic.

### 5. Integration with Core Logic
- The main module must import and invoke the correct functions from the analysis, copy, and verify phases.
- It must ensure that all phases use the same UID/path abstraction for consistency.

### 6. Status, Logging, and Error Handling
- The tool must provide commands to show job status, logs, and errors.
- All errors must be reported to the user with clear messages.
- The tool must exit with a nonzero code on fatal errors.

### 7. Testability
- The CLI and all handler functions must be unit-testable.
- Argument parsing and command dispatch must be separable for direct invocation in tests.

## Design Notes
- All file and directory operations must be robust to cross-platform differences.
- The main module must not contain phase-specific logic; it should delegate to the appropriate phase modules.
- Debug output should be available for all major operations to aid in troubleshooting.

---

This document describes the requirements and design intent for `main.py` in the file copy tool. Each requirement is traceable to a specific function or CLI command in the implementation.
