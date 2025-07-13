# Project Overview and Structure

> **For initial setup and directory-specific bootstrap instructions, see [`agent-bootstrap.md`](./agent-bootstrap.md) in this directory.**

This document consolidates all project-related information, including overview, directory structure, coding conventions, testing, and automation.

---

## Overview

This project uses an **agent-oriented workflow** to manage complex file operations, ensure resumability, and provide full auditability and collaboration. All core process rules, conventions, and standards are documented in the relevant files in `agents/`.

---

## Directory Structure

- **`agents/`**: See [Agent Protocols and Rules](../rules/protocol.md) for details on planning, design, memory, and reasoning files.
- **`changes/`**: Execution logs and persistent state (see separate docs).
- **`fs-copy-tool/`**: Main source code package (Python module: `fs_copy_tool`).

---

## Coding & File Operation Conventions

- Use **block-wise (4KB)** reads for checksum and file copying.
- Never hold critical state in memory—**persist everything to SQLite** and/or the appropriate log/state files in `changes/`.
- Use **volume ID + relative path** for all file identification and matching.
- Do not copy a file if its checksum already exists in the destination.
- All operations must be **resumable, idempotent, and safely interruptible**.
- Use `pathlib` for filesystem operations in Python.
- Log progress, errors, and status messages via the Python `logging` module, not `print`.
- Scripts must be **cross-platform** (Windows + Linux).
- The codebase must remain free of duplicate or obsolete files at all times.
- Refactor and consolidate logic as the project evolves to maintain clarity and maintainability.

---

## Testing, Linting & CI

- All new features/bugfixes require tests in `tests/` mirroring `src/`.
- Run `pytest` (with coverage), `black`, `flake8`, and `mypy` before merging or PR.
- No lint/type errors allowed in main branches.
- PRs must include a "Testing Done" section and reference issues.

---

## Scripts and Taskfile

- `scripts/test.sh` and `scripts/test.ps1`: Run all Python tests
- `scripts/lint.sh` and `scripts/lint.ps1`: Run flake8 linter
- `scripts/black.sh` and `scripts/black.ps1`: Run black code formatter
- `scripts/mypy.sh` and `scripts/mypy.ps1`: Run mypy type checker
- `Taskfile.yml`: Defines all automation tasks for cross-platform use with https://taskfile.dev/

---

_Last updated: 2025-07-12_
