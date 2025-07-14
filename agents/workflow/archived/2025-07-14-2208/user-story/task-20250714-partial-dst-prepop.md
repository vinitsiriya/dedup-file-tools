# Task: Manual Test for Partial Destination Prepopulation

## Steps
1. Set up `.temp/manual_tests/partial_dst_prepop` as the workspace.
2. Create a source directory with files: fileA, fileB, fileC, fileD.
3. Create a destination directory with files: fileA, fileC.
4. Schedule a new job using the tool, adding the source directory.
5. Run the workflow: init, add-source, checksum, copy, status, verify, etc.
6. Observe and record which files are copied and which are skipped.
7. Verify job state, logs, and final destination contents.

## Expected Results
- Only fileB and fileD are copied to the destination.
- fileA and fileC are skipped as they already exist.
- Logs and job state reflect correct actions.

---

Linked user story: story-20250714-partial-dst-prepop.md
