# Task List: Named Jobs and Separate Checksum Database

- [ ] Refactor job initialization to require a job name and create `<job-name>.db`.
- [ ] Update all code to use the job name for the main database file.
- [ ] Move `checksum_cache` to a separate SQLite file (`checksum-cache.db`).
- [ ] Refactor all phases (analyze, checksum, copy, verify, summary) to attach and use the checksum database at runtime.
- [ ] Refactor `ChecksumCache` class to support attached checksum database.
- [ ] Add CLI options to specify checksum database path (default and custom).
- [ ] Update all tests and fixtures to support the new database structure.
- [ ] Provide migration script/command for old jobs to extract and move `checksum_cache`.
- [ ] Update documentation and CLI help for job naming and checksum DB sharing.
- [ ] Verify all acceptance criteria and pass all tests.

---

*Created: 2025-07-17*
*Status: Draft (expand as needed)*
