# User Story Notes

Use this file for notes, clarifications, and discussions related to user stories and tasks.

---

## Notes on Two-Stage Verification Feature
- Shallow verification is fast and checks for basic file attributes (existence, size, last_modified, etc.)
- Deep verification is slower but provides cryptographic assurance by comparing checksums
- Each stage has its own results table for auditability and extensibility
- No changes are made to the main destination_files table schema
- CLI should allow running either or both stages and querying results

---

## Notes on Stateful CLI Feature
- The new stateful CLI will allow users to add sources/files incrementally to a job, supporting more flexible and staged workflows.
- Job state must be robust, auditable, and persist across CLI invocations.
- All phases must be updated to operate on the job state, not just CLI arguments.
- Migration and documentation are critical due to the breaking nature of this change.
- Backward compatibility or migration scripts may be needed for existing jobs.

---

## Notes on Stateful CLI Feasibility
- Only individual files are tracked in the database/job state, not source directories as entities.
- `add-file` and `add-source` (recursive add) are feasible; `list-files` and `remove-file` are feasible.
- `list-sources` and `remove-source` are not feasible without schema changes.
- Document this limitation clearly for users.

---
