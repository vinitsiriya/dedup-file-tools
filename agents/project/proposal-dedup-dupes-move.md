# Proposal: dedup_file_tools_dupes_move Package

## Overview

Introduce a new package `dedup_file_tools_dupes_move` to the project. This package will provide a CLI tool to identify and move all duplicate files from a source directory (or set of directories) to a specified target directory. The tool will be integrated into the project and registered in `setup.py` as a separate CLI entry point.

## Motivation

- Simplify the process of cleaning up duplicate files by moving them to a dedicated location for review or deletion.
- Support large-scale deduplication and organization tasks as part of the file-copy-tool ecosystem.
- Provide a robust, auditable, and resumable workflow for duplicate file management.

## Key Features

- Scan one or more directories for duplicate files (by checksum or content).
- Move all detected duplicates to a user-specified directory, preserving directory structure or flattening as an option.
- CLI interface: `dedup-dupes-move` (or similar), registered in `setup.py`.
- Logging of all actions and errors for auditability.
- Support for dry-run mode to preview actions without making changes.
- Idempotent and safely interruptible operations.
- Cross-platform support (Windows and Linux).

## Implementation Plan

1. Create the `dedup_file_tools_dupes_move` package with appropriate module structure.
2. Implement core logic for duplicate detection and file moving.
3. Add CLI interface and argument parsing.
4. Integrate logging and dry-run support.
5. Register the CLI tool in `setup.py`.
6. Write tests and documentation.

## Open Questions

- What criteria should be used for duplicate detection (checksum, name, size, etc.)?
- Should the tool support interactive or batch modes?
- How should conflicts (e.g., name collisions in the target directory) be handled?

---

_This is a draft proposal for review and iteration._
