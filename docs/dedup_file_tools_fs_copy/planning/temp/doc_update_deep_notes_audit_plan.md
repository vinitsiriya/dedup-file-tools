# Code Files/Modules to Review

- fs_copy_tool/main.py (CLI, job/DB logic, argument parsing)
- fs_copy_tool/db.py (DB schema, initialization)
- fs_copy_tool/utils/checksum_cache.py (Checksum DB logic)
- fs_copy_tool/phases/copy.py (Copy logic, DB usage)
- fs_copy_tool/phases/verify.py (Verification logic, DB usage)
- fs_copy_tool/utils/uidpath.py (UID/path logic)
- tests/ (all test files for CLI and DB usage examples)
- scripts/ (any scripts referencing DBs or CLI usage)

# ...existing content...
# Per-File Audit & Update Checklist

## README.md
- [ ] Update all references to job DB naming (`{job_name}.db` instead of `copytool.db`).
- [ ] Update CLI usage examples to include `--job-name`.
- [ ] Document the separation of main job DB and checksum DB.
- [ ] Remove or update any legacy/obsolete instructions.

## docs/cli.md
- [ ] Ensure all CLI command examples use `--job-name` and correct DB names.
- [ ] Add notes about the new DB structure and required arguments.

## docs/index.md
- [ ] Update architecture overview to reflect new DB separation.
- [ ] Update any workflow diagrams or descriptions.

## docs/requirements.md
- [ ] Ensure requirements reflect the new job/DB structure and CLI changes.

## docs/requirements-summary-feature.md
- [ ] Update for new DB and CLI requirements.

## docs/requirements-test.md
- [ ] Ensure all test requirements reference the correct DB and CLI usage.

## docs/unit-tests.md
- [ ] Update any test instructions or examples for new DB/CLI structure.

## docs/integration-tests.md
- [ ] Ensure integration test docs use correct DB/CLI structure.

## docs/manual-tests.md
- [ ] Update manual test instructions for new DB/CLI structure.

## docs/uidpath.md
- [ ] Check for any references to old DB/CLI usage.

## docs/agent-bootstrap.md
- [ ] Update for new architecture if relevant.

## docs/article_auditable_agent_bootstrap.md
- [ ] Audit for any legacy references.

## docs/external_ai_tool_doc.md
- [ ] Check for DB/CLI references.

## docs/doc_audit_tasklist.md
- [ ] Add/update audit tasks for new structure.

## docs/requirements/deep-verify-feature.md
- [ ] Ensure feature doc matches new DB/CLI structure.

## docs/requirements/shallow-verify-feature.md
- [ ] Ensure feature doc matches new DB/CLI structure.

## docs/requirements/summary-feature.md
- [ ] Ensure feature doc matches new DB/CLI structure.

---
Add more per-file notes as you proceed.
# Documentation Deep Notes & Audit Plan

## Audit Plan
- Review all documentation for references to job DB naming, CLI usage, and architecture.
- Identify any legacy instructions, screenshots, or code snippets that reference old DB names or omit `--job-name`.
- Check for consistency in terminology: "job DB", "checksum DB", "job name", etc.
- Ensure all CLI command examples use the new required arguments and file names.
- Verify that requirements, test, and architecture docs reflect the new separation of main job DB and checksum DB.
- Note any areas where migration or upgrade instructions are needed for users of previous versions.
- Document any new or changed behaviors, especially around job initialization, DB creation, and CLI workflows.

## Deep Notes
- The main job DB is always `{job_name}.db` in the job directory.
- The checksum DB is always `checksum-cache.db` in the job directory, never named after the job.
- All CLI commands that operate on a job require `--job-name` (mandatory for all workflows).
- The schema for both DBs is initialized at job creation; all tables are present from the start.
- Tests and code are now fully compliant with the new architecture; all legacy code paths have been removed.
- Any documentation or code referencing `copytool.db` or missing `--job-name` is outdated and must be updated.
- CLI usage, test instructions, and requirements must all reflect the new architecture and naming.
- If users are upgrading from an older version, they must migrate their DBs or re-initialize jobs to match the new structure.

## Checklist (Deep)
- [ ] Audit all CLI command examples for correct arguments and file names
- [ ] Audit all architecture diagrams and explanations for DB separation
- [ ] Audit all requirements and test docs for compliance with new structure
- [ ] Audit for any remaining legacy references or obsolete instructions
- [ ] Prepare migration/upgrade notes for users
- [ ] Document any new error messages or behaviors

---
Add more deep notes and audit steps as you proceed.
