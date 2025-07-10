# AGENTS.md

## Overview

This project uses an **agent-oriented workflow** to manage complex file operations, ensure resumability, and provide full auditability and collaboration.  
All core process rules, conventions, and standards are documented here.  
The `agents/` directory contains all active and historical agent planning, design, memory, and communication artifacts.

---

## 1. Directory Structure

- **`agents/`**: Planning, design, memory, and reasoning for agents and humans.
- **`changes/`**: Execution logs and persistent state (see separate docs).
- **`fs-copy-tool/`**: Main source code package (Python module: `fs_copy_tool`).

#### `agents/` files:
| File              | Purpose                                                             |
|-------------------|---------------------------------------------------------------------|
| `task.md`         | The immediate task (single actionable item, updated as you go)      |
| `strategy.md`     | Solution reasoning, architecture choices, and implementation notes  |
| `todos.md`        | Backlog/future improvements not part of this run                    |
| `notes.md`        | Raw logs, scratchpad, and brainstorming by agent or human           |
| `questions.md`    | List of open questions for clarification or future investigation    |
| `assumptions.md`  | Working assumptions (system state, drive rules, etc)                |
| `glossary.md`     | Key domain/project terms and their definitions                      |
| `checkpoints.md`  | Key progress points, resets, or decision boundaries                 |
| `research.md`     | References, external links, and sample code snippets                |
| `review.md`       | Human feedback, code/arch reviews, pair-programming notes           |
| `decisions.md`    | Finalized key decisions (architecture, algorithms, format changes)  |

---

## 2. General Rules for Agents

- **Read `AGENTS.md`** before each session.
- Start with the current actionable item in `agents/task.md`.
- Consult `strategy.md` for the reasoning and chosen approach.
- Maintain and update all relevant `agents/` files as work progresses.
- Log all open questions and assumptions (update or resolve as needed).
- Regularly checkpoint progress in `checkpoints.md` for resumability.
- Any change in plan, workflow, or protocol must be immediately reflected in the relevant task lists and planning files (e.g., `agents/task.md`, `agents/micro-task.md`).
- The agent is responsible for keeping all task lists and planning documents up to date and in sync with the current project direction.
- Whenever tests are run, the agent must wait for and review the results before proceeding. All outcomes (pass/fail/errors) must be logged and acted upon as needed.
- After running tests, the agent must:
  1. Wait for test completion and collect all results.
  2. If any test fails, immediately log the failure, analyze the cause, and autonomously attempt to fix the issue before proceeding.
  3. Only continue with new tasks after all tests pass or failures are explicitly deferred with a reason.
- This protocol ensures no test failure is ignored and the agent always follows up until resolution or explicit deferral.
- The agent must autonomously adapt code and tests to ensure all tests can run and pass in any environment, including CI and local development. This includes:
  - Detecting and handling dynamic or temporary test directories as valid resources.
  - Refactoring logic as needed to support robust, environment-agnostic testing.
  - Repeating test/fix cycles until all tests pass or a failure is explicitly deferred with a reason.
- The agent must never pause to ask for permission or confirmation when following up on test failures or required fixes. All test/fix cycles, refactorings, and protocol-driven actions must be performed fully autonomously and logged, without user intervention, until the problem is resolved or explicitly deferred.
- The agent must never narrate or announce future actions. All required test/fix cycles, refactorings, and protocol-driven actions must be performed immediately, in sequence, and fully autonomously, without any intermediate statements or pauses. Only log or report after the fact, not before.

---

## 3. Coding & File Operation Conventions

- Use **block-wise (4KB)** reads for checksum and file copying.
- Never hold critical state in memory—**persist everything to SQLite** and/or the appropriate log/state files in `changes/`.
- Use **volume ID + relative path** for all file identification and matching.
- Do not copy a file if its checksum already exists in the destination.
- All operations must be **resumable, idempotent, and safely interruptible**.
- Use `pathlib` for filesystem operations in Python.
- Log progress, errors, and status messages via the Python `logging` module, not `print`.
- Scripts must be **cross-platform** (Windows + Linux).

---

## 4. Testing, Linting & CI

- All new features/bugfixes require tests in `tests/` mirroring `src/`.
- Run `pytest` (with coverage), `black`, `flake8`, and `mypy` before merging or PR.
- No lint/type errors allowed in main branches.
- PRs must include a "Testing Done" section and reference issues.

---

## 5. Collaboration and Human + Agent Memory

- Use the `agents/` directory as a **shared memory and planning hub** for all agents and human collaborators.
- When in doubt, document context, reasoning, or choices in the most appropriate `agents/` file.
- Move resolved items from `questions.md` to `notes.md` or `decisions.md` as appropriate.

---

## 6. Example Workflow

1. **Agent or human reviews `task.md`** for next steps.
2. Consults `strategy.md` and other supporting docs for how/why.
3. Works on the task, logging all progress, assumptions, and questions.
4. Periodically checkpoints in `checkpoints.md` and updates `changes/`.
5. After completion, updates `task.md` (mark done, set next task).
6. Refactors or cleans up `todos.md`, `assumptions.md`, and logs as necessary.

---

## 7. Best Practices

- **Be explicit:** Every design choice, edge case, and question should be written down.
- **Audit-friendly:** All changes, logs, and state files should be committed as part of the project history.
- **Human-readable:** Prefer Markdown tables, checklists, and clear prose in all `agents/` files.
- **Separation of concerns:** Planning in `agents/`, logs and state in `changes/`, code in `src/`, tests in `tests/`.

---

## 8. Codebase Cleanliness and Redundancy

- Whenever new code or modules are added, ensure any old, redundant, or superseded files are removed or cleaned up immediately.
- The codebase must remain free of duplicate or obsolete files at all times.
- Refactor and consolidate logic as the project evolves to maintain clarity and maintainability.

---

## 9. File Deletion Protocol

- If a file must be deleted from the repository, create a `delete.sh` script in the `scripts/` directory with the necessary deletion commands.
- Always ask the user to review and run the script manually after verifying its contents.
- Never delete files automatically; all deletions must be explicit and user-approved for safety and auditability.
- The agent will execute `delete.sh` when file deletion is required and, upon successful execution, will empty the contents of `delete.sh` to prevent accidental re-use. Work will then resume as normal.

---

## 10. Testing & Automation Scripts

- All commands for running tests, linting, and other automation should be placed in the `scripts/` directory as executable scripts (e.g., `test.sh`, `lint.sh`).
- The project should also maintain a [Taskfile](https://taskfile.dev/) (`Taskfile.yml`) at the root for standardized, cross-platform task automation.
- For every automation or test script, provide both a `.sh` (Bash) and a `.ps1` (PowerShell) version in the `scripts/` directory to ensure cross-platform compatibility (Linux/macOS and Windows).
- Update and maintain both versions as the project evolves.
- Scripts and Taskfile tasks must be kept up to date as the project evolves.

---

## 11. Micro-Task Tracking & Autonomous Operation

- All micro-tasks, sub-steps, and atomic actions must be logged in `agents/micro-task.md` to ensure nothing is forgotten.
- The agent must work fully autonomously, tracking every step and sub-step, and never omitting required actions or context.
- Use `micro-task.md` as a running checklist and scratchpad for granular progress.

---

## 12. Agent Planning File Archival & Workspace Freshness

- After each major commit, milestone, or significant work session, all agent `.md` planning and log files in `agents/` must be archived.
- Archive location: `agents/backup/YYYY-MM-DD-HHMM/` (date and time-stamped).
- Only the current, active `.md` files remain in `agents/` for the next session—reset to template/heading state.
- Archival is performed via `archive_agents.sh` and `archive_agents.ps1` scripts in `scripts/`.
- The agent must prompt the user to run the archival script after each major commit.
- This ensures a clean, focused workspace for new work, and a full, immutable history for audit and review.

---

## 13. Requirements Checklist

- All requirements from `requirements.md` must be tracked in `agents/requirements-checklist.md` as a running checklist.
- Each item is marked complete only after full implementation and verification.
- The checklist must be updated as requirements evolve or new ones are added.
- Use this file for audit, review, and milestone tracking.

---

## 21. Requirement Proposal, Strategy, and Cleanup Protocol

- Every new or changed requirement must start with a proposal in `agents/proposals/requirement-YYYYMMDD-shortdesc.md`.
- For each accepted proposal, create an implementation strategy in `agents/strategy/requirement-YYYYMMDD-shortdesc.md`.
- Once the requirement is fully implemented, tested, and verified:
  - Archive the proposal and strategy files to a date-stamped directory under `agents/backup/`.
  - Delete the originals from `agents/proposals/` and `agents/strategy/`.
- This keeps the workspace clean and focused, while preserving all history for audit.

---

## Proposal Refinement

- During the proposal refinement stage, the agent must:
  - Only update the proposal file (`agents/proposals/...`) with clarifications, discussion, and refinements.
  - Do not update requirements.md, requirements-checklist.md, or task files until the proposal is explicitly marked as "Accepted" or "Ready for implementation" in the proposal file.
  - Once accepted, proceed to update all other documentation and begin implementation.
- This ensures a clear separation between proposal refinement and implementation, preventing confusion or premature changes.

---

## Scripts and Taskfile

- `scripts/test.sh` and `scripts/test.ps1`: Run all Python tests
- `scripts/lint.sh` and `scripts/lint.ps1`: Run flake8 linter
- `scripts/black.sh` and `scripts/black.ps1`: Run black code formatter
- `scripts/mypy.sh` and `scripts/mypy.ps1`: Run mypy type checker
- `Taskfile.yml`: Defines all automation tasks for cross-platform use with https://taskfile.dev/

---

## 14. Agent Resume Protocol

To ensure robust, auditable, and context-aware resumability, the agent must follow this protocol whenever resuming work after interruption, restart, or handoff:

1. **Read All Planning, Requirements, Proposal, and CLI Structure Files**  
   - Read all `.md` files in the `agents/` directory (`task.md`, `checkpoints.md`, `notes.md`, `assumptions.md`, `todos.md`, `questions.md`, `decisions.md`, `strategy.md`, etc.).
   - **Read all proposal files in `agents/proposals/` and strategy files in `agents/strategy/` to capture any new, accepted, or pending requirements.**
   - Read project-level requirements and design files outside `agents/`, such as `requirements.md` and any other relevant documentation at the project root.
   - **Review the CLI structure and all CLI-related code and documentation (including job directory logic and commands such as `init`, `import-checksums`, etc.) to ensure alignment with requirements and planning.**
   - Synthesize the current actionable item, open questions, assumptions, requirements, proposals, CLI structure, and the last checkpoint.

2. **Assess Directory, File State, and CLI/Job Directory Implementation**  
   - Use CLI tools (e.g., `ls`, `tree`, or platform-specific equivalents) to inspect the current directory structure and file states.
   - **On Windows, the agent MUST run:**
     ```powershell
     Get-ChildItem -Recurse -File -Name | Where-Object { $_ -notmatch 'venv|pycache|.git|.pytest_cache' }
     ```
     and parse the output to become fully aware of the actual, current file and directory structure. This step is mandatory for every resume.
   - Compare the actual workspace state with the documented checkpoints, planning files, requirements, proposals, and CLI/job directory implementation.
   - Identify any changes, new files, or discrepancies since the last checkpoint.

3. **Load Persistent State**  
   - Load the persistent state from SQLite and/or log/state files in `changes/` to determine progress and status of all operations.
   - **If a job directory is used (per requirements), ensure all state, logs, planning files, and CLI logic are loaded from and point to that directory.**
   - **If importing checksums from an old database is required, ensure the import phase is completed before resuming copy/checksum operations.**

4. **Align and Update Context**  
   - Update internal state, planning files, and CLI/job directory logic to reflect the actual state of the workspace.
   - Log any discrepancies, new context, or decisions in `agents/notes.md` and update `agents/checkpoints.md` as needed.

5. **Resume from Last Checkpoint**  
   - Resume operations from the last successful checkpoint, processing only incomplete or pending items.
   - Ensure all actions are consistent with the latest planning, documentation, requirements, proposals, CLI structure, job directory logic, and actual workspace state.
   - **If new requirements or proposals (e.g., job directory, checksum import, CLI changes) are present in `requirements.md` or `agents/proposals/` but not yet implemented, log this in `agents/notes.md` and update the plan before proceeding.**

6. **Log and Document Progress**  
   - Log all resumed actions, updates, and encountered issues in the appropriate `.md` files.
   - After resuming, run all relevant tests and log results, following up on any failures as required by protocol.

**Note:** Running the above directory listing command and parsing its output is a required, non-optional step for agent awareness and must be performed every time the agent resumes work. Failure to do so is a protocol violation.

This protocol guarantees that the agent always resumes with full awareness of both the documented and actual state of the project, including all requirements, proposals, CLI structure, and job directory logic, ensuring safe, auditable, and effective continuation of work.

---

_Last updated: 2025-07-10_

