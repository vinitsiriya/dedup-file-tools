# Manual Tests for dedup_file_tools_compare

## Purpose
Manual tests are used for interactive or exploratory testing of the compare feature, especially for scenarios not easily automated.

## Location & Organization
- Manual test scripts: `manual_tests/dedup_file_tools_compare/` (each scenario in its own subdirectory)
- Fixture generator: `manual_tests/dedup_file_tools_compare/<scenario>/generate_fixtures_manual.py`
- **All manual test operations should be performed in the `.temp/manual_tests/dedup_file_tools_compare/` directory to avoid polluting the main workspace.**

## How to Run
- On Windows, run the relevant script in `manual_tests/dedup_file_tools_compare/<scenario>/` in PowerShell.
- Use the provided fixture generator to create test directories and files.

## Guidelines
- Organize manual tests by scenario for clarity and scalability.
- Use manual tests to verify CLI feedback, logging, and edge cases.
- Record observations and issues in the appropriate planning or log files.
- Use manual tests to validate new features before automating them.
- Always perform manual test operations in the `.temp/manual_tests/dedup_file_tools_compare/` directory.

## Example Scenario: Simple Directory Compare
- See `manual_tests/dedup_file_tools_compare/simple_scenario/simple_manual_test.ps1` for a full workflow test.
- This scenario covers: fixture generation, init, add-to-left, add-to-right, find-missing-files, show-result.

## Extending
- Add new manual test scripts in the appropriate `manual_tests/dedup_file_tools_compare/` directory for each scenario as needed.
- Document manual test procedures and expected outcomes in this file or in the planning docs.

---
To add more scenarios, copy and adapt scripts in the appropriate `manual_tests/dedup_file_tools_compare/` directory.
