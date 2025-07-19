# Plan: dedup_file_tools_dupes_move Documentation Update

## Goal
Update all documentation for the `dedup_file_tools_dupes_move` module to match the new generic documentation agent protocol and directory structure.

## Steps

1. Carefully read the CLI (main.py, cli.py, handlers.py) and all CLI argument definitions and help text.
2. Make detailed notes in implementation strategies (dev-notes.md, agent-context.md) about CLI options, argument patterns, and any edge cases or special behaviors.
3. Audit the code line by line, especially CLI, handler, and phase logic, to ensure all features and options are documented.
4. Update documentation files section by section, line by line, with no mistakes or omissions:
   - requirements/features/<feature>.md
   - implementation/<feature>.md
   - feature/<feature>.md
5. Update global requirements and test docs:
   - requirements/requirements.md
   - requirements/requirements-test.md
6. Update CLI and external tool docs if needed:
   - user_prepective/cli.md
   - standalone/external_ai_tool_doc.md
7. Update README.md if relevant.
8. Note any files reviewed but not changed.
9. Use agent context file to track reminders and protocol.

## Checklist
- [ ] requirements/features docs updated
- [ ] implementation docs updated
- [ ] feature docs updated
- [ ] requirements.md updated
- [ ] requirements-test.md updated
- [ ] cli.md updated (if needed)
- [ ] external_ai_tool_doc.md updated (if needed)
- [ ] README.md updated (if needed)
- [ ] All changes follow protocol and naming conventions
- [ ] Unchanged files noted

# Documentation Update Plan: dedup_file_tools_dupes_move

This plan follows a multi-iteration, focused approach to ensure all documentation for `dedup_file_tools_dupes_move` is accurate, protocol-compliant, and auditable.

## Iteration 1: Requirements & Features Foundation
- Update/create requirements, requirements-test, and feature docs in `docs/dedup_file_tools_dupes_move/developer_reference/requirements/`.
- Map requirements to features and test cases.
- Validate against CLI/code for completeness.

## Iteration 2: Implementation & CLI Details
- Update implementation.md and cli.md for architecture, workflow, and CLI accuracy.
- Cross-check CLI docs with code and help output.

## Iteration 3: Agent & Protocol Integration
- Update external_ai_tool_doc.md for agent/AI tool integration and protocol compliance.
- Ensure agent context, plan, and dev-notes are up to date in this directory.

## Iteration 4: Review & Audit
- Review all docs for protocol compliance, accuracy, and clarity.
- Audit for missing/outdated sections.
- Update README.md to reflect the current structure.

## Iteration 5: Final Validation & Archival
- Validate docs against codebase and tests.
- Archive previous versions if needed.
- Log actions and update agent-context.md/dev-notes.md with a summary.

---

See also: `docs/dedup_file_tools_dupes_move/developer_reference/doc_update_plan.md` for the full protocol and checklist.
