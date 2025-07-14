# fileops.md - Requirements Documentation for fileops.py

## Purpose
This module provides low-level file operations for the file copy tool, including copying files, verifying file integrity, and computing checksums.

## Key Requirements

### 1. File Copy
- The tool must support copying files from a source to a destination, in blocks, with optional progress reporting.
- The copy operation must preserve file modification times (mtime).
- The copy must be robust to interruptions and always restart the file if interrupted.

### 2. Checksum Calculation
- The tool must provide a function to compute the SHA-256 checksum of a file, reading in blocks for efficiency.
- The checksum function must work for files of any size and be robust to I/O errors.

### 3. File Verification
- The tool must provide a function to verify that two files have identical content by comparing their checksums.

### 4. Progress and Callbacks
- The copy operation must support optional progress callbacks and per-file progress bars for user feedback.

### 5. Testability
- All file operations must be unit-testable, with tests verifying correct copy, checksum, and verification behavior.

---

This document describes the requirements and design intent for `fileops.py` in the file copy tool. Each requirement is traceable to a specific function or workflow step in the implementation.
