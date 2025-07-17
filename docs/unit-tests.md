# Unit Tests Documentation

## Purpose
Unit tests verify the correctness of individual modules and functions in isolation.

## Location
- All unit tests are located in the `tests/` directory.
- Example files: `test_utils.py`, `test_phases.py`, `test_import_checksums.py`, `test_jobdir.py`.


## How to Run
- Use the provided scripts:
  - On Linux/macOS: `./scripts/test.sh`
  - On Windows: `./scripts/test.ps1`
- Or run directly with pytest:
  - `pytest tests/`

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.

## Guidelines
- Each test should be independent and not rely on external state.
- Use fixtures for setup/teardown as needed.
- Ensure all new code is covered by unit tests.

## Extending
- Add new test files in `tests/` following the naming convention `test_*.py`.
- Reference the module or function under test in the test file docstring.

## Stateful CLI Unit Testing
- Unit tests should cover helper functions for file addition, removal, and listing in the job state/database.
- Ensure all new code for stateful CLI is covered by unit tests.
- Directory-level state is not supported; unit tests must operate at the file level.
