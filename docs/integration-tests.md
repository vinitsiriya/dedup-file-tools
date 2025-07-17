# Integration Tests Documentation

## Purpose
Integration tests verify that multiple components work together as expected, including CLI workflows and database interactions.

## Location
- Integration tests are found in both `tests/` and `e2e_tests/` directories.
- Example files: `test_cli.py`, `test_cli_workflow.py`, `e2e_tests/test_e2e_cases.py`, `e2e_tests/test_e2e_fixtures.py`.


## How to Run
- Use the provided scripts:
  - On Linux/macOS: `./scripts/test.sh`
  - On Windows: `./scripts/test.ps1`
- Or run directly with pytest:
  - `pytest tests/`
  - `pytest e2e_tests/`

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.

## Guidelines
- Integration tests may use fixture generators (`scripts/generate_fixtures.py`).
- Cover CLI commands, workflow phases, and database state transitions.
- Ensure tests are robust and clean up after themselves.

## Extending
- Add new integration or E2E test files in `tests/` or `e2e_tests/`.
- Document any new workflows or scenarios covered.

## Stateful CLI Integration
- Integration tests must cover the new file-level stateful CLI commands (`add-file`, `add-source`, `list-files`, `remove-file`).
- Workflows should demonstrate incremental job setup and correct operation of all phases after file addition/removal.
- Directory-level state is not supported; integration tests must operate at the file level.
