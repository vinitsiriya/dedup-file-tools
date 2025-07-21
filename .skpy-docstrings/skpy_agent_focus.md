# skpy Agent Docstring Focus Guide

This document provides guidance for writing high-quality docstrings in skeleton (.skpy) files for the dedup-file-tools project. Use these focus points to ensure docstrings are clear, useful, and aligned with project design and implementation strategies.

---

## 1. Module-Level Docstring
- State the purpose and responsibilities of the module (e.g., phase, handler, utility).
- Summarize the high-level workflow and key features.
- Mention any important design goals (deduplication, resumability, auditability, performance).

## 2. Function/Class Docstrings
- Clearly state the function/class purpose and its role in the workflow.
- List all parameters and return values, including types and meaning.
- Describe the high-level implementation logic (main steps, not just what it does).
- Explain how the function interacts with the database, pools, or other modules.
- Note error handling, edge cases, and logging.
- Mention threading/concurrency if relevant.
- Add extensibility or future-proofing notes if applicable.

## 3. Database/Schema-Related Functions
- Specify what tables/fields are accessed or modified.
- Describe how schema changes or migrations are handled.

## 4. Phase/Workflow Functions
- Explain how the function fits into the overall phase-based workflow.
- State what phase it represents and how progress/status is tracked.

## 5. Result/Reporting Functions
- Describe the type of output generated (summary, full report, CSV/JSON).
- Explain how output location is determined (job dir, user-specified, etc.).
- Note any filtering, sorting, or formatting logic.

## 6. Concurrency/Performance
- Document use of threads, processes, or batch operations.
- Explain how thread safety and database access are managed.

## 7. Error Handling and Logging
- Describe how errors are reported and logged.
- Explain how the system recovers from or retries failed operations.

---

## Example (for a checksum phase function)

"""
Computes or updates checksums for all files in the specified table (e.g., source_files or destination_files).

- Loads file list from the given table in the database.
- Uses ThreadPoolExecutor to parallelize checksum computation, with each thread using its own DB connection.
- Updates the checksum cache in the shared commons DB.
- Reports progress using tqdm if enabled.
- Handles errors and logs any issues encountered during processing.
"""

---

Use this guide as a checklist when writing or reviewing docstrings in .skpy skeleton files. This ensures consistency, clarity, and alignment with the dedup-file-tools architecture and best practices.
