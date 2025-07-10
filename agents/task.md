# Task: Implement Resume & Retry Logic and Main Orchestration

- [x] Ensure tool resumes and retries pending/error files using database state
- [x] Implement main script to orchestrate all phases (analysis, checksum, copy)
- [x] Add CLI entry point for user
- [x] Log and checkpoint progress

---

# Task: Implement Import Checksums and Job Directory Management

- [x] Implement CLI `init` command to create and initialize a job directory
- [x] Update all phases to use the job directory for state, logs, and planning files
- [x] Implement CLI `import-checksums` command to import checksums from an old SQLite database
- [x] Implement logic to match files by (uid, relative_path, size, last_modified) and copy checksum values
- [x] Add/Update CLI commands for `analyze`, `checksum`, `copy`, `resume`, `status`, and `log`/`audit` to use the job directory
- [x] Add tests for job directory management and checksum import
- [x] Add tests for new CLI commands: `resume`, `status`, `log`/`audit`
- [x] Update documentation and usage instructions
- [x] Log all actions and decisions in checkpoints.md

---

# Task: Prepare Project for Publishing as a Python Package

- [x] Add `setup.py` and `setup.cfg` for packaging
- [x] Add `pyproject.toml` for build system requirements (PEP 517/518 compliance)
- [ ] Ensure `requirements.txt` is up to date and referenced in `setup.py`
- [ ] Update `README.md` with installation and PyPI usage instructions
- [ ] Add classifiers, metadata, and entry points for CLI in `setup.py`
- [ ] Verify all scripts and modules are included/excluded as needed
- [ ] Add or update MANIFEST.in if needed
- [x] Test package build and install locally
- [ ] Log all actions and decisions in checkpoints.md and notes.md

---

_Next step: Begin packaging setup and update documentation._

