# Manual Tests Documentation

## Purpose
Manual tests are used for interactive or exploratory testing, especially for scenarios not easily automated.

## Location
- Manual test scripts: `manual_test.ps1`
- Fixture generator for manual tests: `scripts/generate_fixtures_manual.py`
- **All manual test operations should be performed in the `.temp` directory to avoid polluting the main workspace.**

## How to Run
- On Windows, run `manual_test.ps1` in PowerShell.
- Use `generate_fixtures_manual.py` to create custom test directories and files in `.temp`.

## Guidelines
- Use manual tests to verify UI/CLI feedback, logging, and edge cases.
- Record observations and issues in the appropriate planning or log files.
- Use manual tests to validate new features before automating them.
- Always perform manual test operations in the `.temp` directory.

## Extending
- Update or add new manual test scripts as needed.
- Document manual test procedures and expected outcomes in this file or in the planning docs.
