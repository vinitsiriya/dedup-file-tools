# Requirement Proposal: dedup_file_tools_dupes_move

## Title
Deduplication Utility: Move Duplicate Files by Checksum

## Date
2025-07-18

## Status
Draft

## Context
Users often accumulate duplicate files (identical content, different names/locations) within large directory trees. Efficiently identifying and removing these duplicates is essential for storage management and data hygiene.

## Requirement
Develop a new Python package `dedup_file_tools_dupes_move` that:
- Scans a user-specified directory (recursively) for files with identical checksums (content-based duplicates).
- Identifies all duplicate files (files with the same checksum, regardless of name or location).
- Moves all but one copy of each duplicate group to a user-specified destination directory, preserving directory structure as needed.
- Provides a CLI for user interaction, with options for dry-run, logging, and summary output.
- Ensures all operations are resumable, idempotent, and auditable (logs all actions).
- Handles errors gracefully and provides clear user feedback.

## Constraints
- Must use block-wise reading for checksums (do not load entire files into memory).
- Must work cross-platform (Windows, Linux).
- Must not delete files automatically—only move duplicates to the destination directory.
- Must log all actions and errors for auditability.
- Must not move files if the destination already contains a file with the same checksum.
- Must be compatible with the project's agent protocols and logging standards.

## Out of Scope
- Deletion of files (user must manually delete after review).
- Deduplication across multiple root directories in a single run (single root per invocation).

## Acceptance Criteria
- CLI tool finds and moves duplicate files as described.
- All actions are logged and resumable.
- No data loss or accidental overwrites occur.
- User can review moved files in the destination directory before deletion.

---

_This proposal is a draft and requires review and feedback before implementation._
