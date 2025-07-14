# Feasibility Analysis: Stateful CLI for Incremental Source/File Addition

**Date:** 2025-07-14
**Author:** User

## Context
The accepted proposal for a stateful CLI includes commands like `add-source`, `add-file`, `list-sources`, and `remove-source`. However, the current design maintains only individual files in the database, not high-level source directory records.

## Analysis

### Current State
- The database schema tracks individual files (with volume ID, relative path, etc.), not source directories as entities.
- All operations (analyze, copy, etc.) are performed at the file level.
- There is no persistent list of source directories; only files discovered during analysis are tracked.

### Implications
- **add-file**: Feasible. Individual files can be added to the database/job state.
- **add-source**: Feasible as a convenience command to recursively add all files from a directory, but the directory itself is not tracked as an entity.
- **list-sources / remove-source**: Not feasible under the current schema, since source directories are not stored or referenced after analysis. Only files are tracked.
- **list-files / remove-file**: Feasible. Users can list or remove individual files from the job state.

### Options
- **Option 1: Minimal Change**
  - Implement only `add-file`, `add-source` (as recursive add), `list-files`, and `remove-file`.
  - Document that source directories are not tracked as entities.
- **Option 2: Schema Change**
  - Add a new table to track source directories, enabling true `list-sources` and `remove-source` commands.
  - Requires more invasive changes and migration.

### Recommendation
- Proceed with Option 1 for now: implement file-level stateful commands only.
- Clearly document the limitation and rationale in user documentation and CLI help.
- Revisit schema changes if user demand for directory-level operations arises.

## Conclusion
- The stateful CLI is feasible at the file level.
- Directory-level tracking is not supported without schema changes.
- Adjust proposal, user story, and tasks to reflect this reality.

---

_This analysis is submitted for review and further planning._
