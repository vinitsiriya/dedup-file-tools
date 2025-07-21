# Requirement Proposal: dedup_file_tools_compare Module

## Title
Add a File Pool Comparison Module: `dedup_file_tools_compare`

## Status
Draft

## Author
AI Agent

## Date
2025-07-21

---

## Overview


This proposal introduces a new module, `dedup_file_tools_compare`, to the dedup-file-tools project. This module will enable robust and efficient comparison between two directories (or pools) of files, specifically by comparing file checksums. Users will be able to quickly identify files that are identical, different, or unique to each directory based on checksum values. The module will offer both CLI and API interfaces, and will seamlessly integrate with the existing phase-based workflow for maximum flexibility and automation.

**Design Note:**
The module will maintain two pool tables, named **left** and **right**, for all operations and reporting. All comparisons, outputs, and user interfaces will refer to these as the canonical sources for comparison.

---

## Motivation

- Enable verification of migration, backup, or deduplication completeness between two pools.
- Support audit, reconciliation, and advanced sync workflows.
- Provide a reusable, modular tool for comparing file sets by UID, path, and content.

---

## Requirements

- Accept two pools as input (directories, database tables, or job states).
- Compare files by UID, relative path, and optionally checksum, size, and last modified time.
- Output:
  - Files unique to each pool
  - Files with matching paths but differing content
  - Files that are identical in both pools
- Support both CLI and API usage.
- Integrate with the existing logging and progress reporting conventions.
- Designed for extensibility (future: multi-pool, advanced diff, reporting).

---

## User Stories

- As a user, I want to compare two backup directories and see which files are missing, changed, or identical.
- As an agent, I want to verify that a deduplication or migration job has produced a complete and correct result.
- As a developer, I want to use a simple API to compare two file pools in my own scripts.

---

## Implementation Notes

- The module will be named `dedup_file_tools_compare` and reside at the top level of the project.
- It will provide both a CLI entry point and a Python API.
- It will use the existing UID/path abstraction and database schema where possible.
- Output will be available as console, CSV, or JSON.
- The module will be fully tested and documented.

---

## Out of Scope

- Multi-way (more than two pools) comparison (future work)
- Automated sync or merge (future work)

---

## Acceptance Criteria

- The module can compare two pools and output unique, changed, and identical files.
- CLI and API interfaces are available and documented.
- Tests cover all major use cases.

---

## Status
Draft – Awaiting feedback and refinement.

---

## Next Steps
- Review and refine requirements with stakeholders.
- Approve proposal for implementation.
- Begin design and development upon approval.
