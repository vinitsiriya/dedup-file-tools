# Strategy: Migration to Stateful CLI for Incremental Source/File Addition

**Date:** 2025-07-14
**Author:** User

## Context
The proposal for a stateful CLI (see `requirement-20250714-stateful-cli.md`) introduces breaking changes to how sources/files are managed and how users interact with the tool. This requires careful documentation, migration planning, and a thorough analysis of all affected features and workflows.

## Migration & Compatibility Strategy

### 1. Documentation
- Clearly document the new workflow in the README and CLI help text.
- Provide migration notes for users upgrading from the old CLI (single-command, stateless usage).
- Include examples for both incremental and legacy workflows (if supported).

### 2. Feature Impact Analysis
- **CLI commands:** All commands that accept `--src` or `--file` must be reviewed and updated to use the new job state.
- **Job state management:** New logic for persisting, listing, and removing sources/files must be robust and auditable.
- **Phases:** All phases (analyze, checksum, copy, verify, etc.) must operate on the current job state, not just CLI arguments.
- **Tests:** All tests must be updated or added to cover incremental workflows and ensure backward compatibility (if any).
- **Error handling:** Ensure clear errors for missing or invalid job state.

### 3. Migration Plan
- Implement new stateful commands (`add-source`, `add-file`, etc.) alongside existing commands for a transition period.
- Deprecate direct `--src`/`--file` arguments in favor of job state after sufficient notice.
- Provide a migration script or helper to convert old job directories to the new format if needed.

### 4. Communication
- Announce the breaking change in release notes and documentation.
- Highlight benefits and new workflows for users.

## Acceptance Criteria
- All affected features and commands are updated and tested.
- Documentation and migration notes are clear and complete.
- Users are guided through the transition with minimal disruption.

---

_This strategy is submitted for review and further planning._
