# Strategy: Refactor Copy Status to a Separate Table

## Overview
This document outlines the step-by-step strategy for refactoring the file copy status logic to use a dedicated `copy_status` table, as described in the requirement proposal.

## Steps

1. **Schema Refactor**
   - Remove `copy_status`, `last_copy_attempt`, and `error_message` from `source_files` and `destination_files` tables.
   - Create a new `copy_status` table:
     - Columns: `uid`, `relative_path`, `role` (`source` or `destination`), `copy_status`, `last_copy_attempt`, `error_message`
     - Primary key: (`uid`, `relative_path`, `role`)

2. **Codebase Update**
   - Update all code to use the new `copy_status` table for status, error, and attempt info.
   - Refactor all status-related queries, inserts, and updates to reference the new table.
   - Update all joins and logic that previously used status fields in the file tables.

3. **Migration**
   - Write a migration script to move all existing status data from `source_files` and `destination_files` into the new `copy_status` table.
   - Ensure no data is lost and all status is preserved.

4. **Testing**
   - Update all test setup and assertions to use the new table.
   - Add/extend tests to verify correct migration and status handling.

5. **Documentation**
   - Update any relevant documentation to reflect the new schema and logic.

## Notes
- All code and tests must be updated before removing the old fields to avoid breakage.
- Migration must be atomic and auditable.
- All status logic must be verified for both `source` and `destination` roles.

---

*This strategy is subject to review and refinement. Please check off each step in the checklist as you proceed.*
