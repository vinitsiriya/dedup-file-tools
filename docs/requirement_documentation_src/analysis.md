# analysis.md - Requirements Documentation for analysis.py

## Purpose
This module implements the analysis phase of the file copy workflow. It scans source and destination volumes, extracts file metadata, and registers files in the job database using a system-independent UID and relative path abstraction.

## Key Requirements

### 1. Volume Scanning
- The tool must scan all files under each user-supplied source or destination root.
- For each file, it must determine the UID (using UidPath) and a relative path (relative to the mount point).
- The scan must be robust to symbolic links, hidden files, and cross-platform differences.

### 2. Metadata Extraction
- For each file, the tool must extract and record size and last modification time.
- All metadata must be stored in the job database in the appropriate table (source_files or destination_files).

### 3. UID/Path Abstraction
- The UID and relative path must be determined using UidPath.convert_path for every file.
- The relative path must be treated as opaque outside of UidPath logic.

### 4. Database Integration
- The tool must insert or update file records in the database, ensuring no duplicates for the same (uid, rel_path).
- The schema must support efficient lookup and update by (uid, rel_path).

### 5. Progress Reporting
- The analysis phase must report progress to the user, including the number of files scanned and indexed.
- Logging and debug output must be available for troubleshooting.

### 6. Error Handling
- The tool must handle inaccessible files, permission errors, and missing volumes gracefully.
- Errors must be logged and not halt the entire analysis unless critical.

### 7. Testability
- The analysis phase must be unit- and integration-testable, with tests verifying correct UID/path extraction and DB updates.

---

This document describes the requirements and design intent for `analysis.py` in the file copy tool. Each requirement is traceable to a specific function or workflow step in the implementation.
