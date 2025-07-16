# Requirement Proposal: Move Copy Status to a Separate Table

## Summary

This proposal aims to normalize the database schema by moving the copy status and related fields out of the `source_files` and `destination_files` tables into a dedicated `copy_status` table. This change will improve maintainability, extensibility, and clarity of status management for file copy operations.

## Motivation

Currently, the fields `copy_status`, `last_copy_attempt`, and `error_message` are embedded in both `source_files` and `destination_files`. This leads to schema duplication, complicates status management, and makes future extensions (such as multi-stage status or audit trails) more difficult. Decoupling status from file metadata will:

- Improve schema normalization
- Simplify status updates and queries
- Enable future extensibility (e.g., multi-stage status, audit logs)

## Requirements

1. **Create a new table `copy_status`:**
    - Columns: `uid`, `relative_path`, `role` (`source` or `destination`), `copy_status`, `last_copy_attempt`, `error_message`
    - Primary key: (`uid`, `relative_path`, `role`)
    - Foreign keys: (`uid`, `relative_path`) referencing `source_files` or `destination_files` as appropriate

2. **Remove status fields from file tables:**
    - Remove `copy_status`, `last_copy_attempt`, and `error_message` from both `source_files` and `destination_files`.

3. **Update all code and queries:**
    - All status-related logic must use the new `copy_status` table.
    - All inserts, updates, and selects for status must reference the new table.

4. **Migration:**
    - Provide a migration script to move existing status data to the new table.
    - Ensure no data is lost during migration.

5. **Testing:**
    - Update all tests to use the new schema and status logic.
    - Add tests to verify correct migration and status handling.

## Acceptance Criteria

- The schema is normalized: status is managed only in the `copy_status` table.
- All code and tests are updated to use the new table.
- Migration preserves all existing status data.
- No regressions in copy, status, or error handling logic.

---

*This proposal is subject to review and refinement. Please provide feedback or request clarifications as needed before marking as Accepted or Ready for implementation.*
