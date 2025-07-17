## Argument Details: Required, Optional, and Defaults

The one-shot command must clearly distinguish between required and optional arguments, and define default behaviors for all optional arguments:

### Required Arguments
- `--job-dir` (Path to the job directory. Must be provided.)
- `--job-name` (Name of the job/database. Must be provided.)
- `--src` (Source directory or volume root(s). Must be provided.)
- `--dst` (Destination directory or volume root(s). Must be provided.)

### Optional Arguments and Defaults
- `--log-level` (Default: `INFO`) — Controls logging verbosity. If not set, standard info-level logging is used.
- `--threads` (Default: `4`) — Number of threads for parallel operations. If not set, uses 4 threads.
- `--no-progress` (Default: `False`) — If set, disables progress bars. By default, progress bars are shown.
- `--resume` (Default: `True` for copy phase) — If set, resumes incomplete jobs by skipping already completed files. Always enabled for copy.
- `--reverify` (Default: `False`) — If set, forces re-verification of all files in verify/deep-verify phases.
- `--checksum-db` (Default: `<job-dir>/checksum-cache.db`) — Custom path for checksum DB. If not set, uses the default location in the job directory.
- `--other-db` (Optional) — Path to another compatible SQLite database for importing checksums. If not set, no import is performed.
- `--table` (Default: `source_files` for checksum phase) — Table to use for checksumming. If not set, defaults to source files.
- `--stage` (Default: `shallow` for verify phase) — Verification stage. If not set, shallow verification is performed.
- `--skip-verify` (Default: `False`) — If set, skips verification steps.
- `--deep-verify` (Default: `False`) — If set, performs deep verification after shallow verification.
- `--dst-index-pool` (Optional, default: value of `--dst`) — Path to destination index pool. If not set, the value of `--dst` will be used as the destination index pool.
- Any other options present in the existing commands should be treated as optional unless otherwise specified.

If an optional argument is not provided, the default behavior (as described above) will be used. The command must validate required arguments and provide clear error messages if any are missing.
# Requirement Proposal: One-Shot End-to-End Workflow Command

## Title
Add a "one-shot" command to the CLI for a seamless, end-to-end file copy and verification workflow

## Status
Draft

## Date
2025-07-17

## Author
GitHub Copilot

---

## Problem Statement

Currently, users must execute a long sequence of CLI commands to complete a standard file copy and verification workflow. For example, a typical PowerShell automation script may look like:

```powershell
Run-Step "fs-copy-tool init --job-dir $JobDir --job-name $JobName" "Initialize job"
Run-Step "fs-copy-tool import-checksums --job-dir $JobDir --job-name $JobName --other-db $OtherDb" "Import checksums"
Run-Step "fs-copy-tool add-source --job-dir $JobDir --job-name $JobName --src $SrcDir" "Add source directory"
Run-Step "fs-copy-tool add-to-destination-index-pool --job-dir $JobDir --job-name $JobName --dst $DstIndexPool" "Add destination index pool"
Run-Step "fs-copy-tool analyze --job-dir $JobDir --job-name $JobName --src $SrcDir --dst $DstDir" "Analyze"
Run-Step "fs-copy-tool checksum --job-dir $JobDir --job-name $JobName --table source_files" "Checksums (source)"
Run-Step "fs-copy-tool checksum --job-dir $JobDir --job-name $JobName --table destination_files" "Checksums (destination)"
Run-Step "fs-copy-tool copy --job-dir $JobDir --job-name $JobName --src $SrcDir --dst $DstDir" "Copy"
Run-Step "fs-copy-tool verify --job-dir $JobDir --job-name $JobName --stage shallow" "Verify (shallow)"
Run-Step "fs-copy-tool verify --job-dir $JobDir --job-name $JobName --stage deep" "Verify (deep)"
Run-Step "fs-copy-tool status --job-dir $JobDir --job-name $JobName" "Status"
```

This approach is cumbersome, error-prone, and not user-friendly, especially for new users or for automation.


## Proposed Solution


Introduce a new CLI command (e.g., `one-shot` or `run-all`) that performs the entire workflow in a single invocation. This command will:

  - Accept all required arguments up front (e.g., `--job-dir`, `--job-name`, `--src`, `--dst`, etc.).
  - Accept all optional and advanced arguments that are available in the current multi-step workflow, including but not limited to:
    - `--log-level` (set logging verbosity)
    - `--threads` (number of threads for parallel operations)
    - `--no-progress` (disable progress bars)
    - `--resume` (resume incomplete jobs, default True for copy)
    - `--reverify` (force re-verification in verify/deep-verify)
    - `--checksum-db` (custom checksum DB path)
    - `--other-db` (for importing checksums)
    - `--table` (for checksum phase: source_files or destination_files)
    - `--stage` (for verify: shallow or deep)
    - `--skip-verify`, `--deep-verify` (to control verification steps)
    - All required paths: `--job-dir`, `--job-name`, `--src`, `--dst`, `--dst-index-pool`
    - Any future options added to subcommands
    - Any other options present in the existing commands (e.g., add-file, add-source, etc.)
  - Ensure that all features and configuration options available in the current workflow are accessible through the one-shot command, so users do not lose any flexibility or control.
  - Internally execute the following steps in order:
    1. Initialize the job directory and databases.
    2. Optionally import checksums from another database.
    3. Add the source directory and destination index pool.
    4. Analyze source and destination volumes.
    5. Compute checksums for source and destination files.
    6. Copy files, resuming as needed.
    7. Run verification (shallow and/or deep).
    8. Print a summary and status report.
  - Allow users to skip or customize steps via flags as above.


## User Experience Goals

- Greatly simplify the user experience for common workflows.
- Reduce the risk of missing steps or misconfiguring jobs.
- Make automation and scripting easier (replace multi-step scripts with a single command).
- Provide a clear, auditable, and repeatable process for end-to-end file copy and verification.

## Example Usage

```powershell
fs-copy-tool one-shot --job-dir $JobDir --job-name $JobName --src $SrcDir --dst $DstDir --dst-index-pool $DstIndexPool --import-checksums $OtherDb --deep-verify
```

## Acceptance Criteria

- A new CLI subcommand is available that performs the full workflow as described.
- All required arguments are accepted and validated up front.
- Each step is executed in sequence, with robust error handling and logging.
- Users can customize or skip steps as needed.
- The new command is documented in the CLI documentation.
- The implementation is covered by automated tests.

## Out of Scope

- Changes to the underlying copy, checksum, or verification logic (unless required for integration).
- Major refactoring of unrelated CLI commands.

## References
- See `main.py` for current CLI structure and workflow.
- See `docs/cli.md` for CLI documentation requirements.

---

**Status:** Draft. Please review and provide feedback or request refinements as per the workflow protocol.
