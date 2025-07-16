# Strategy: Named Jobs and Separate Checksum Database

## 1. Job Naming and Database File Naming
- Refactor job initialization to require a job name.
- Main job database file should be named `<job-name>.db`.
- Update all code to use the job name for the database path.

## 2. Separate Checksum Database
- Move `checksum_cache` table to a separate SQLite file, `checksum-cache.db`.
- Attach the checksum database to the job database at runtime using SQLite's `ATTACH DATABASE`.
- All checksum cache operations must use the attached database.
- Add CLI options to specify checksum database path (default: `checksum-cache.db` in the job directory, user-overridable).

## 3. Code Refactor
- Update all code that references `checksum_cache` to use the attached database.
- Ensure all phases use the correct database connections.
- Update tests and documentation.

## 4. Backward Compatibility
- Provide migration/fallback logic for old jobs.
- Document migration process.

## 5. User Experience
- Update CLI help and docs for job naming and checksum DB sharing.
- Provide clear error messages for missing/incompatible checksum DB.

## 6. Phase and Utility Refactor
- All phases (analyze, copy, verify, summary) must attach the checksum database at runtime using SQLite's `ATTACH DATABASE`.
- All queries and updates to the checksum cache must reference the attached DB (e.g., `checksum_db.checksum_cache`).
- The `ChecksumCache` class must be refactored to accept a connection with the attached checksum DB, or manage its own connection logic.
- CLI and job state logic must be updated to pass both job DB and checksum DB paths.
- Update all tests and fixtures to support the new DB structure.

## 7. Migration
- Provide a script/command to extract `checksum_cache` from old job DBs and move it to a new `checksum-cache.db` file.

---

*Created: 2025-07-17*
*Status: Draft (expand as code is analyzed)*
