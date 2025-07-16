# Strategy Notes: Named Jobs and Separate Checksum Database

- Current code assumes a single `copytool.db` per job, with all tables (including `checksum_cache`) in one file.
- All job state and workflow logic reference the job database via `job_dir/copytool.db`.
- The `ChecksumCache` class and all checksum logic use the main job database.
- To support a separate checksum database, all code that uses `checksum_cache` must be updated to use an attached database.
- SQLite's `ATTACH DATABASE` allows referencing tables in the attached DB as `attached_db.table_name`.
- CLI and job config must track both the job DB and the checksum DB.
- Tests and fixtures will need to be updated to create and attach the checksum DB as needed.
- Migration: For existing jobs, provide a script/command to extract and move the checksum cache to a new file.
- All phases (analyze, copy, verify, summary) currently open the main job DB directly and expect all tables to be present.
- To support a separate checksum DB, every phase that needs checksums must attach the checksum DB at runtime and reference it by alias.
- The summary and verify phases will need to be updated to use the attached checksum DB for any checksum-related queries.
- The migration script must copy the `checksum_cache` table from old job DBs to the new checksum DB.
- UidPath/UidPathUtil utilities are independent and do not require changes for this refactor.

---

*Created: 2025-07-17*
*Status: Draft (expand as code is analyzed)*
