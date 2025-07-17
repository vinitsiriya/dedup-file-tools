# Proposal: Named Jobs and Separate Checksum Database

## Summary
Introduce named jobs, where each job has a unique name and its own database file named `<job-name>.db`. Additionally, decouple the checksum cache into a separate database file (`checksum-cache.db`) that can be attached and shared across multiple jobs. This will allow for efficient reuse of checksum data, reducing redundant computation and making the tool more flexible and performant.

## Motivation
- **Job Organization:** Named jobs make it easier to manage, identify, and archive job runs.
- **Checksum Sharing:** A separate checksum database allows sharing and reusing checksums across jobs, saving time and computation.
- **Flexibility:** Users can attach/detach checksum databases as needed, supporting workflows with shared or portable checksum caches.
- **Performance:** Avoids recalculating checksums for files already processed in other jobs.

## Requirements
- Each job must have a unique name, provided at creation/init time.
- The main job database file must be named `<job-name>.db` instead of the default `copytool.db`.
- The checksum cache must be stored in a separate SQLite database file, `checksum-cache.db`.
- The tool must support attaching the checksum database to the job database at runtime using SQLite's `ATTACH DATABASE`.
- All checksum cache operations must use the attached checksum database.
- The user must be able to specify which checksum database to use (default: `checksum-cache.db` in the job directory, but can be any path).
- The tool must support sharing a single checksum database across multiple jobs.
- Documentation and CLI help must be updated to reflect the new workflow.

## Implementation Strategy (to be detailed in strategy file)
- Update job initialization to require a job name and create `<job-name>.db`.
- Refactor code to use the job name for the main database file.
- Refactor checksum cache logic to use an attached database (`checksum-cache.db`).
- Add CLI options to specify checksum database path.
- Update all relevant code, tests, and documentation.

## Acceptance Criteria
- Jobs are created and referenced by name, with database files named accordingly.
- Checksum cache is stored in a separate, attachable database file.
- The tool can attach and use a shared checksum database for multiple jobs.
- All tests pass and documentation is updated.

---

*Created: 2025-07-17*
*Status: Draft (awaiting user feedback)*
