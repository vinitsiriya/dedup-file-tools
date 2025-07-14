# User Story: Partial Destination Prepopulation

## Context
As a user, I want to copy files from a source to a destination where some files already exist at the destination, so that only missing files are copied and duplicates are avoided.

## Scenario
- The destination contains a subset of files from the source.
- The source has additional files not present in the destination.
- A new job is scheduled to copy from source to destination.

## Acceptance Criteria
- Only files not already present at the destination (by checksum) are copied.
- Files already present at the destination are skipped.
- The job state and logs accurately reflect the actions taken.
- The process is resumable and auditable.

---

Linked requirement: requirement-20250714-partial-dst-prepop.md
