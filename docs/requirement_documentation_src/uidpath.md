# uidpath.md - Requirements Documentation for uidpath.py

## Purpose
This module provides a system-independent abstraction for file paths, enabling robust, portable file referencing across different operating systems and environments.

## Key Requirements

### 1. UID Abstraction
- The tool must assign a unique identifier (UID) to each filesystem or mount point (volume serial on Windows, UUID on Linux).
- The UID must be used in place of drive letters or mount points for all file tracking and referencing.

### 2. Relative Path Abstraction
- The tool must convert absolute file paths to a tuple of (UID, relative_path), where relative_path is always relative to the detected mount point.
- The format of relative_path must be treated as opaque outside of UidPath logic.

### 3. Path Reconstruction
- The tool must support reconstructing absolute paths from (UID, relative_path) tuples, provided the volume is available.
- The tool must handle pseudo-mounts for test environments.

### 4. Mount Point Discovery
- The tool must detect all available mount points and their UIDs at initialization.
- The tool must support refreshing the mount point mapping at runtime.

### 5. Cross-Platform Support
- The tool must work on both Windows and Linux, using the appropriate system APIs for each.

### 6. Testability
- All UID/path operations must be unit- and integration-testable, with tests verifying correct conversion and reconstruction.

---

# Requirements: UID Path Abstraction

## Overview
The UID path abstraction must provide a robust, system-independent way to represent file paths. All file-level state in `fs-copy-tool` must be tracked using UIDs, ensuring portability and auditability across platforms and sessions.

## Requirements
- Convert file paths to unique, system-independent UIDs
- All job state (add-file, add-source, remove-file, list-files) must use UIDs
- Enable robust tracking of files even if paths change or drives are remounted
- Use in all phases: analyze, checksum, copy, verify, import
- All operations must be logged for auditability

## Benefits
- Portability: jobs can be resumed on different systems or after drive changes
- Robustness: files are tracked even if their absolute path changes
- Auditability: all file operations are traceable via UIDs

---

This document describes the requirements and design intent for `uidpath.py` in the file copy tool. Each requirement is traceable to a specific method or workflow step in the implementation.
