# Project Workflow Protocol

This directory contains the canonical workflow protocol documentation for the project. The structure is as follows:

- `proposal/requirement/` — Requirement proposals (one file per proposal)
- `proposal/strategy/` — Implementation strategies (one file per strategy)
- `proposal/status.md` — Status tracking for all proposals
- `user-story/story.md` — User stories
- `user-story/task.md` — Tasks derived from user stories
- `user-story/notes.md` — Notes and clarifications
- `user-story/other.md` — Other user story artifacts
- `archived/` — Archived workflow and planning files (date-stamped)

---

## Workflow Rules and Protocols

### Collaboration and Human + Agent Memory

- Use the workflow directory as a **shared memory and planning hub** for all agents and human collaborators.
- When in doubt, document context, reasoning, or choices in the most appropriate file.
- Move resolved items from questions to notes or decisions as appropriate.

---

### Best Practices

- **Be explicit:** Every design choice, edge case, and question should be written down.
- **Audit-friendly:** All changes, logs, and state files should be committed as part of the project history.
- **Human-readable:** Prefer Markdown tables, checklists, and clear prose in all workflow files.
- **Separation of concerns:** Planning in workflow, logs and state in `changes/`, code in `src/`, tests in `tests/`.

---

### Codebase Cleanliness and Redundancy

- Whenever new code or modules are added, ensure any old, redundant, or superseded files are removed or cleaned up immediately.
- The codebase must remain free of duplicate or obsolete files at all times.
- Refactor and consolidate logic as the project evolves to maintain clarity and maintainability.

---

### Requirements Checklist

- All requirements mentioned in the `/docs/` directory must be tracked in a running checklist in this workflow.
- Each item is marked complete only after full implementation and verification.
- The checklist must be updated as requirements evolve or new ones are added.
- Use this checklist for audit, review, and milestone tracking.

---

### Micro-Task Tracking & Autonomous Operation Protocol

- All micro-tasks, sub-steps, and atomic actions must be logged in a running checklist to ensure nothing is forgotten.
- The agent must work fully autonomously, tracking every step and sub-step, and never omitting required actions or context.
- Use the checklist as a running log for granular progress.

---

### Proposal Refinement Protocol

- During the proposal refinement stage, only update the proposal file with clarifications, discussion, and refinements.
- The agent must present each new proposal draft to the user and explicitly ask for feedback or refinements.
- The agent must continue to iterate and refine the proposal based on user feedback, and only proceed after explicit user approval.
- Do not update requirements or task files until the proposal is explicitly marked as "Accepted" or "Ready for implementation" in the proposal file.
- Once accepted, proceed to update all other documentation and begin implementation.
- This ensures a clear separation between proposal refinement and implementation, preventing confusion or premature changes.

---

### Proposal Completion and Archival Protocol

- When a proposal (requirement or strategy) is marked as "Complete":
  - The agent must immediately archive the full proposal file (requirement or strategy) into the appropriate `archived/YYYY-MM-DD-HHMM/` directory, using the current date and time.
  - The agent must update the `proposal/status.md` table to reflect the new status as "Complete".
  - The agent must then **delete the original proposal file** from the `proposal/requirement/` or `proposal/strategy/` directory, so only active (incomplete) proposals remain.
  - The agent must log the archival and deletion action in the commit message or workflow log for traceability.
- Archival and deletion are mandatory and must be performed as soon as a proposal is closed as complete. Failure to archive and delete is a protocol violation.
- The archival and deletion process must be visible and explicit in the agent's workflow, with clear steps and confirmation.

---

## Archival Protocol

- After each major commit, milestone, or significant work session, all workflow and planning `.md` files in this directory must be archived.
- Archive location: `archived/YYYY-MM-DD-HHMM/` (date and time-stamped).
- Only the current, active `.md` files remain in the workflow directory for the next session—reset to template/heading state.
- Archival is performed via scripts (e.g., `archive_agents.sh` and `archive_agents.ps1`) in the `scripts/` directory.
- The agent or user must run the archival script after each major commit.
- This ensures a clean, focused workspace for new work, and a full, immutable history for audit and review.

---

_Last updated: 2025-07-12_
