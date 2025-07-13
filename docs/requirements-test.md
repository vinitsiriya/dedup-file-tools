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
  - Sparse files (if supported)
  - Symlinks, hard links, junctions (handle/skip as needed)
  - Files with different permissions/ownerships (Linux)
  - Files with timestamps in the future or far past
  - Files with no extension or hidden files (dotfiles)
  - Identical names in different directories
- E2E tests MUST:
  - Use the fixture generator to create test directories
  - Run the full CLI workflow (analyze, checksum, copy, status, log) on these fixtures
  - Assert correctness (all files copied, no duplicates, correct checksums, etc.)
  - Cover all automatable edge cases
  - Be robust, repeatable, and clean up after themselves
- Manual test scripts SHOULD optionally use the large/complex fixtures for interactive/manual runs
- All test requirements and protocols in this file are subject to the same agent protocol, archival, and review rules as other requirements and planning files.

## Guidelines and Strategies for Test Requirements

### General Principles
- All automated, stress, and edge-case tests must be reproducible and platform-agnostic (work on Windows and Linux).
- Use parameterized fixture generation to cover a wide range of scenarios and edge cases.
- Prefer automation for all testable cases; document any manual-only edge cases separately.
- Ensure all tests clean up after themselves to avoid polluting the workspace.
- Track all test planning, implementation, and results in the appropriate `agents/` files.

### Fixture Generation Strategy
- Use a single script (`scripts/generate_fixtures.py`) to generate all required test fixtures.
- The script should support command-line options for size, depth, file types, and special cases.
- Document usage in the script docstring and README.
- Update the script as new edge cases or requirements are identified.

### E2E and Stress Test Strategy
- Place E2E tests in `e2e_tests/` for clarity and separation from unit tests.
- E2E tests should:
  - Use the fixture generator to create input data
  - Run the full CLI workflow (analyze, checksum, copy, etc.)
  - Assert that all files are processed correctly and efficiently
  - Cover all automatable edge cases
- Manual test scripts (e.g., `manual_test.ps1`) should optionally use the same fixtures for interactive runs.

### Protocol Compliance
- All test requirements, strategies, and results must be documented and tracked as per agent protocol.
- Archive and update planning files after each major milestone or change.

---

*Created as part of agent constitution amendment on 2025-07-10*
