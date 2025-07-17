# requirements-test.md

This file contains all requirements and protocols for automated, stress, and edge-case testing of the fs-copy-tool project. It is maintained separately from requirements.md to allow detailed tracking and evolution of test-specific requirements, fixtures, and protocols.

- All new or updated test requirements, especially for E2E, large, or complex fixtures, must be documented here.
- requirements.md will reference this file for all test-related requirements.
- This file is subject to the same agent protocol and archival rules as other requirements and planning files.

## Automated, Stress, and Edge-Case Testing Requirements
- A fixture generator script MUST exist (see `scripts/generate_fixtures.py`) to create large, complex, and edge-case file/directory structures for testing.
- The fixture generator MUST support:
  - Deeply nested directories
  - Long file names and paths
  - Large files (100s MBs/GBs)
  - Many small files (10,000+)
  - Duplicate files (same content, different names/paths)
  - Special characters, Unicode, reserved names in filenames
  - Read-only files or directories
  - Identical names in different directories
- E2E and integration tests MUST:
  - Use the fixture generator to create test directories
  - Be robust, repeatable, and clean up after themselves
- Manual test scripts SHOULD optionally use the large/complex fixtures for interactive/manual runs
- All test requirements and protocols in this file are subject to the same agent protocol, archival, and review rules as other requirements and planning files.

## CLI and Feature Test Coverage Requirements
- All CLI commands and options must have corresponding automated tests:
  - All commands require `--job-name` and use `<job-name>.db` for the job database.
  - The checksum cache database is always `checksum-cache.db` in the job directory.
  - `init`, `import-checksums`, `analyze`, `checksum`, `copy`, `resume`, `status`, `log`,
  - `add-file`, `add-source`, `list-files`, `remove-file`
- Tests MUST cover:
  - Resume/copy logic (partial, missing, already copied, corrupted files)
  - Edge cases for all supported platforms
  - File-level stateful setup and teardown
  - UID abstraction and checksum cache fallback
- All features and edge cases must be covered by automated tests and kept up-to-date with code changes.

## Test Scenario Checklist
| Scenario                                 | Required Test Type(s)         |
|------------------------------------------|------------------------------|
| Init job directory                       | Unit, E2E                    |
| Add/remove/list files                    | Unit, E2E                    |
| Analyze source/destination               | Unit, E2E                    |
| Checksum phase (all options)             | Unit, E2E                    |
| Copy phase (all options, resume, dedup)  | E2E, Integration             |
| Resume interrupted/failed jobs           | E2E, Integration             |
| Import checksums (from checksum_cache)   | Unit, E2E                    |
| Verification (shallow/deep, all options) | E2E, Integration             |
| Status/log/audit commands                | E2E, Integration             |
| Edge cases (corruption, partial, etc.)   | E2E, Integration, Manual     |
| Fixture generator coverage               | Unit, E2E                    |
| Error handling/reporting                 | Unit, E2E, Integration       |

## Guidelines and Strategies for Test Requirements
- All automated, stress, and edge-case tests must be reproducible and platform-agnostic (work on Windows and Linux).
- Use parameterized fixture generation to cover a wide range of scenarios and edge cases.
- Prefer automation for all testable cases; document any manual-only edge cases separately.
- Ensure all tests clean up after themselves to avoid polluting the workspace.
- Track all test planning, implementation, and results in the appropriate `agents/` files.

## Stateful CLI Testing Requirements (2025-07-15)
- All CLI and E2E tests MUST cover the new file-level stateful commands:
  - `add-file`, `add-source`, `list-files`, `remove-file`
- Tests MUST verify incremental job setup, file addition/removal, and correct operation of all phases after stateful setup.
- Directory-level state is NOT supported; tests must operate at the file level.
- Update and maintain all test scripts and documentation to reflect this breaking change.

---

*Created as part of agent constitution amendment on 2025-07-10*
