# User Story: One-Shot End-to-End Workflow Command

## Title
As a user, I want a single `one-shot` command that performs the entire file copy and verification workflow, so that I can complete jobs with a single, simple command.

## Status
Draft

## Date
2025-07-17

## Author
GitHub Copilot

---

## User Story

**As a** user of the file copy tool,
**I want** to run a single command that performs all the necessary steps for a complete copy and verification job,
**so that** I do not have to remember or script multiple commands, and can avoid mistakes or omissions.

---

## Acceptance Criteria

- I can run a `fs-copy-tool one-shot` command with all required arguments (`--job-dir`, `--job-name`, `--src`, `--dst`).
- I can provide optional arguments (e.g., `--log-level`, `--threads`, `--no-progress`, `--resume`, `--reverify`, `--checksum-db`, `--other-db`, `--table`, `--stage`, `--skip-verify`, `--deep-verify`, `--dst-index-pool`).
- If I do not provide an optional argument, the tool uses the documented default value.
- If I do not provide `--dst-index-pool`, the tool uses the value of `--dst` as the default.
- The command performs all workflow steps in order: init, (optional) import checksums, add source, add destination index pool, analyze, checksums, copy, verify (shallow/deep), summary.
- I receive clear error messages if any required arguments are missing.
- I receive clear, user-friendly output and logs for each step.
- I can skip or customize steps using flags (e.g., `--skip-verify`, `--deep-verify`).
- The command is documented in the CLI help and user documentation.

---

## Notes
- This user story is based on the requirement proposal for the one-shot command.
- All options and defaults must match the proposal and current CLI conventions.
- The implementation must be covered by automated tests.

---

**Status:** Draft. Please review and provide feedback or request refinements as per the workflow protocol.
