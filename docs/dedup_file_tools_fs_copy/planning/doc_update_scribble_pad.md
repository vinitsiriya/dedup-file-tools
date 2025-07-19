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
- [ ] Update all references to job DB naming in documentation
- [ ] Update CLI usage examples to include `--job-name`
- [ ] Document the separation of main job DB and checksum DB
- [ ] Ensure all test and requirements docs reflect the new architecture
- [ ] Remove or update any legacy/obsolete instructions
- [ ] Add migration/upgrade notes if relevant

---
Add more notes here as you discover more documentation points to update.
