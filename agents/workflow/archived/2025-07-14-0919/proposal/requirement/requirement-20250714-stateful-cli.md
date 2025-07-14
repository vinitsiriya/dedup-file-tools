# Proposal: Stateful CLI for Incremental Source/File Addition

**Date:** 2025-07-14
**Author:** User
**Status:** Accepted (2025-07-14)

## Problem
The current CLI requires all source directories or files to be specified at the time of running commands like `analyze` or `copy`. This is limiting for workflows where sources/files become available over time, or when users want to build up a job incrementally before running operations.

## Proposal
- Introduce new CLI commands to allow incremental addition of sources or files to a job directory, such as:
  - `add-source --job-dir <dir> --src <SRC_ROOT>`
  - `add-file --job-dir <dir> --file <FILE_PATH>`
- Maintain a persistent list of sources/files in the job state (e.g., in the job directory or database).
- Allow users to run `analyze`, `copy`, etc., after all desired sources/files have been added.
- Support listing and removing sources/files from the job state.
- Update documentation and help text to describe the new workflow.

## Rationale
- Enables more flexible, real-world workflows where sources/files are not all known up front.
- Supports large or staged copy jobs, and collaborative or multi-session job setup.
- Reduces user error and improves usability for complex copy tasks.

## Acceptance Criteria
- Users can add sources/files incrementally to a job via CLI.
- The job state persists the list of sources/files.
- All phases (analyze, copy, etc.) operate on the current job state.
- Users can list and remove sources/files from the job state.
- Documentation and tests are updated.

---

_This proposal is accepted and ready for implementation as of 2025-07-14._
