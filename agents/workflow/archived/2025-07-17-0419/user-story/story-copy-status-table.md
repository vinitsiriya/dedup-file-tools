# User Story: Copy Status Table Refactor

## Title
Refactor copy status and error tracking to a dedicated table for normalization and maintainability

## As a...
Developer/maintainer of the file copy tool

## I want...
All file copy status, error, and attempt tracking to be managed in a normalized `copy_status` table, rather than embedded in `source_files` and `destination_files`.

## So that...
- The schema is normalized and easier to maintain
- Status logic is consistent and extensible
- Future features (e.g., audit trails, multi-stage status) are easier to implement

## Acceptance Criteria
- All status and error fields are removed from file tables and managed in the new table
- All code and tests are updated to use the new table
- Migration preserves all existing status data
- No regressions in copy, status, or error handling logic
- All documentation and CLI help is updated

---

See related proposal, strategy, and checklist files for detailed requirements and steps.
