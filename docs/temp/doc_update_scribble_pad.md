# Documentation Update Scribble Pad

## Files to Update
- README.md
- docs/cli.md
- docs/index.md
- docs/requirements.md
- docs/requirements-summary-feature.md
- docs/requirements-test.md
- docs/unit-tests.md
- docs/integration-tests.md
- docs/manual-tests.md
- docs/uidpath.md
- docs/agent-bootstrap.md
- docs/article_auditable_agent_bootstrap.md
- docs/external_ai_tool_doc.md
- docs/doc_audit_tasklist.md
- docs/requirements/deep-verify-feature.md
- docs/requirements/shallow-verify-feature.md
- docs/requirements/summary-feature.md

## Key Changes to Document
- All job DBs are now named `{job_name}.db` instead of `copytool.db`.
- Checksum DB is always `checksum-cache.db` in the job directory.
- All CLI commands that operate on a job require `--job-name`.
- Schema changes: all required tables are created in the main job DB and checksum DB.
- Tests and code are now fully compliant with the named job and separate checksum DB architecture.
- Any references to legacy DB names or missing `--job-name` must be updated.


## Checklist
- [x] Audit code for legacy DB names and missing `--job-name` (all code compliant)
- [x] Audit tests for correct usage (all test logic compliant)
- [x] Update `docs/cli.md` CLI examples for DB names and `--job-name`
- [ ] Review README, index, requirements, and all other docs for indirect references, diagrams, and examples
- [ ] Review test documentation/comments for legacy references
- [ ] Document the separation of main job DB and checksum DB
- [ ] Remove or update any legacy/obsolete instructions
- [ ] Add migration/upgrade notes if relevant

## Deeper Notes (from audit)
- Only `docs/cli.md` had a direct legacy reference; all other docs/code are structurally compliant but should be reviewed for indirect/implicit references.
- All CLI commands in code require `--job-name` and use the new DB naming.
- Test suite is fully compliant, but documentation and comments should be double-checked.

---
Add more notes here as you discover more documentation points to update.
