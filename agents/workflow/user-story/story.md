# User Stories

Document user stories here. Each story should describe a user goal or scenario relevant to the project.

---

## User Story: Robust Two-Stage Verification for File Copy Tool

**Summary:**
As a user, I want the file copy tool to provide a robust, auditable two-stage verification process after copying files, so that I can be confident all files are present, uncorrupted, and match the source.

**Acceptance Criteria:**
- The tool must support a shallow verification stage that checks for file existence, size, and last_modified match.
- The tool must support a deep verification stage that checks file content by recomputing and comparing checksums.
- All verification results must be recorded in dedicated tables for each stage.
- The process must be auditable and results queryable for troubleshooting.
- No schema changes to the main destination_files table.

**Motivation:**
Data integrity and auditability are critical for large-scale file migrations. A two-stage verification process ensures both fast attribute-based checks and deep cryptographic assurance.

---

## User Story: Robust File-Level Resume and Online Checksum for File Copy Tool

**Summary:**
As a user, I want the file copy tool to safely resume interrupted copy operations at the file level and verify file integrity online during the copy, so that I never lose progress and always have confidence in data integrity.

**Acceptance Criteria:**
- The tool must track which files have been fully copied and allow resuming from the last good file after interruption.
- The tool must calculate and verify running checksums for both source and destination during copy.
- If a mismatch is detected during copy, the tool must retry the file or flag an error.
- All file copy status and checksum data must be stored in the database for auditability and robust resume.
- The feature must be covered by automated and manual tests.

**Motivation:**
Large file copies are often interrupted. Users need a reliable way to resume and verify integrity at the file level without starting over, ensuring trust in the copy process.

---

## User Story: Stateful CLI for Incremental File Addition (File-Level Only)

**Summary:**
As a user, I want to incrementally add individual files (or all files from a directory) to a copy job using the CLI, so that I can build up complex or staged copy jobs over time before running analysis or copy operations. Directory-level tracking is not supported.

**Acceptance Criteria:**
- The CLI provides commands to add files to a job state (e.g., `add-file`, `add-source` as recursive add).
- The job state persists the list of files for later operations.
- Users can list and remove individual files from the job state.
- All phases (analyze, copy, etc.) operate on the current job state.
- Documentation and tests are updated to reflect the new workflow and limitations.

**Motivation:**
This enables more flexible, real-world workflows at the file level, supporting large or staged copy jobs, and reduces user error for complex tasks. Directory-level operations are not supported without schema changes.
