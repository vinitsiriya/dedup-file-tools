# Manual Tests Documentation

## Purpose
Manual tests are used for interactive or exploratory testing, especially for scenarios not easily automated.

## Location
- Manual test scripts: `manual_tests/` (each scenario in its own subdirectory)
- Fixture generator for manual tests: `scripts/generate_fixtures_manual.py`
- **All manual test operations should be performed in the `.temp/manual_tests/` directory to avoid polluting the main workspace.**

## How to Run
- On Windows, run the relevant script in `manual_tests/<scenario>/` in PowerShell.
- Use `generate_fixtures_manual.py` to create custom test directories and files in the appropriate workspace (e.g., `.temp/manual_tests/<scenario>`).

## Guidelines
- Use manual tests to verify UI/CLI feedback, logging, and edge cases.
- Record observations and issues in the appropriate planning or log files.
- Use manual tests to validate new features before automating them.
- Always perform manual test operations in the `.temp/manual_tests/` directory.

## Extending
- Add new manual test scripts in the `manual_tests/` directory for each scenario as needed.
- Document manual test procedures and expected outcomes in this file or in the planning docs.

## Stateful CLI Manual Testing
- Manually test the new file-level stateful CLI commands:
  - `add-file`, `add-source`, `list-files`, `remove-file`
- Verify incremental job setup, file addition/removal, and correct operation of all phases after stateful setup.
- Directory-level state is not supported; manual tests must operate at the file level.

## Example Scenarios
- Each subdirectory in `manual_tests/` can cover a different scenario:
  - Deduplication, file addition/removal, copy/resume, verification, interruption/recovery
  - Deeply nested directories, long filenames, special characters, etc.
  - Performance and correctness with large files
  - ...add more as needed
- To add more scenarios, copy and adapt scripts in the `manual_tests/` directory.
