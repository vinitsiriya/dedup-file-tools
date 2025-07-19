## 2025-07-19: Iteration 5 — Final Validation & Archival

- [x] Validated documentation against the latest codebase and test suite.
- [x] Archived previous versions if needed.
- [x] Logged all actions and updated agent-context.md and dev-notes.md with a summary of changes.

---
## 2025-07-19: Iteration 4 — Review & Audit

- [x] Reviewed all documentation for protocol compliance, accuracy, and clarity.
- [x] Audited for missing sections, outdated information, or inconsistencies.
- [x] Updated README.md to reflect the current documentation structure and protocol.

---
## 2025-07-19: Iteration 3 — Agent & Protocol Integration

- [x] Updated external_ai_tool_doc.md for agent/AI tool integration and protocol compliance.
- [x] Ensured agent context, plan, and dev-notes are up to date in agents/workflow/implementation-strategies/dedup_file_tools_dupes_move_doc_update/.

---
## 2025-07-19: Iteration 2 — Implementation & CLI Details

- [x] Updated implementation.md and cli.md for architecture, workflow, and CLI accuracy in docs/dedup_file_tools_dupes_move/developer_reference/.
- [x] Cross-checked CLI docs with code and help output.

---
## 2025-07-19: Iteration 1 — Requirements & Features Foundation

- [x] Created/updated requirements.md, requirements-test.md, features/feature_list.md, and features/feature_details.md in docs/dedup_file_tools_dupes_move/developer_reference/requirements/.
- [x] Mapped requirements to features and test cases.
- [x] Validated requirements and features against CLI/code for completeness.

---
# Dev Notes: dedup_file_tools_dupes_move Documentation Update


## 2025-07-19: Documentation Update Plan

- Adopted a multi-iteration, focused protocol for updating all documentation (see plan.md and docs/dedup_file_tools_dupes_move/developer_reference/doc_update_plan.md).
- Each iteration targets a specific aspect: requirements/features, implementation/CLI, agent/protocol, review/audit, and final validation.
- All actions and changes are logged here for auditability.

---
- Review all changes for protocol compliance before marking the task complete.

## CLI Structure and Options (from main.py)

- **Global options:**
  - `--log-level` (default: INFO)
  - `--config` (YAML config file)

- **Subcommands:**
  - `init`: Initialize a new deduplication job
    - `--job-dir` (required)
    - `--job-name` (required)
  - `add-to-lookup-pool`: (Optional) Add a folder to the lookup pool for duplicate scanning
    - `--job-dir` (required)
    - `--job-name` (required)
    - `--lookup-pool` (required)
  - `analyze`: Scan the lookup pool, compute checksums, and group duplicates
    - `--job-dir` (required)
    - `--job-name` (required)
    - `--lookup-pool` (required)
    - `--threads` (default: 4)
  - `preview-summary`: Preview planned duplicate groups and moves
    - `--job-dir` (required)
    - `--job-name` (required)
  - `move`: Move duplicate files to the dupes folder (or remove)
    - `--job-dir` (required)
    - `--job-name` (required)
    - `--lookup-pool` (required, source folder)
    - `--dupes-folder` (required, destination/removal folder)
    - `--threads` (default: 4)
  - `verify`: Verify that duplicates were moved/removed as planned
    - `--job-dir` (required)
    - `--job-name` (required)
    - `--lookup-pool` (required, source folder)
    - `--dupes-folder` (required, destination/removal folder)
    - `--threads` (default: 4)
  - `summary`: Print summary and generate CSV report of deduplication results
    - `--job-dir` (required)
    - `--job-name` (required)
  - `one-shot`: Run the full deduplication workflow in one command
    - `--job-dir` (required)
    - `--job-name` (required)
    - `--lookup-pool` (required)
    - `--dupes-folder` (required)
    - `--threads` (default: 4)

- **Notes:**
  - All subcommands require `--job-dir` and `--job-name`.
  - `add-to-lookup-pool` is a no-op for now (handled in analyze phase).
  - `move` and `verify` require both source (`--lookup-pool`) and destination (`--dupes-folder`).
  - `one-shot` runs all phases in order.
  - YAML config can override CLI args if provided.

- **Handlers:**
  - Each subcommand is mapped to a handler in handlers.py.
  - Handlers call phase modules for actual logic.

- **Edge Cases:**
  - If a required argument is missing, argparse will show help and exit.
  - If a file is missing during move, it is logged as an error but does not crash.
  - If a file is corrupted or missing during verify, it is logged as an error.

- **See also:** main.py, handlers.py for full argument and handler mapping.
