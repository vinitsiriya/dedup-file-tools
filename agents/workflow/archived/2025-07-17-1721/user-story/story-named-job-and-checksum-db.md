# User Story: Named Jobs and Separate Checksum Database

## As a user
I want to create jobs with a unique name and have the job database named `<job-name>.db`, and I want the checksum cache to be stored in a separate, attachable database (`checksum-cache.db`). This will allow me to share and reuse checksums across jobs, saving time and computation, and making the tool more flexible and efficient.

### Acceptance Criteria
- I can specify a job name when creating a new job, and the main database file is named accordingly.
- The checksum cache is stored in a separate database file (`checksum-cache.db`).
- The tool attaches the checksum database at runtime and uses it for all checksum operations.
- I can specify which checksum database to use for a job (default or custom path).
- I can share a single checksum database across multiple jobs.
- All phases (analyze, checksum, copy, verify, summary) work with the new database structure.
- All tests pass and documentation is updated.

---

*Created: 2025-07-17*
*Status: Draft (awaiting task breakdown)*
