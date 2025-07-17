# agents-protocol.md (dedup_file_tools_dupes_move)

This file defines agent-specific protocol tweaks and behavioral rules for the deduplication tool. It is intended to guide agent operation throughout the user story and implementation process.


## Protocol Tweaks
- Always use `UidPath` for file identification and movement.
- Never manipulate or interpret `rel_path` outside of `UidPath` utilities.
- All file operations must be logged and auditable.
- The agent must halt and log any operation that would result in data loss or overwrite.
- The agent must provide a dry-run mode for all destructive or irreversible actions.
- The agent must ensure resumability and idempotency for all operations.
- The agent must log and surface all errors, warnings, and skipped files.
- The agent must provide a CLI command for audit log review.
- The agent must follow all project-wide agent protocols and workflow rules.

## Commons Migration Protocol (Agent-Specific)
- If any file or utility is to be moved to or refactored into the `dedup_file_tools_commons` package, the agent must NOT perform the move or refactor.
- Such changes must always be performed using a full-featured IDE (e.g., PyCharm) by a human collaborator, to ensure all references and imports are updated correctly.
- The agent should log and notify the user to use an IDE for such changes, and must not attempt automated moves or refactors for commons migration.

## Usage
- Reference this file in all user stories, implementation plans, and code reviews for `dedup_file_tools_dupes_move`.
- Update this file as new agent behaviors or protocol tweaks are required during the project lifecycle.
