# Proposal: Manual Test Scenario — Partial Destination Prepopulation

## Purpose
Test the behavior of the tool when the destination already contains some files that are also present in the source, but the source has additional files not present in the destination. The scenario will schedule a new job and observe what happens.

## Steps
1. Prepare a workspace in `.temp/manual_tests/partial_dst_prepop`.
2. Create a source directory with several files (e.g., fileA, fileB, fileC, fileD).
3. Create a destination directory with a subset of those files (e.g., fileA, fileC).
4. Schedule a new job using the tool, adding the source directory.
5. Run the workflow (init, add-source, checksum, copy, status, verify, etc.).
6. Observe and record:
   - Which files are copied
   - Which files are skipped (already present)
   - The correctness of job state, logs, and final destination contents

## Expected Outcome
- Only files not already present at the destination (by checksum) should be copied.
- Files already present at the destination should be skipped.
- The job state and logs should accurately reflect the actions taken.

## Discussion
This scenario tests deduplication and resumability logic when the destination is partially prepopulated. It is important for real-world incremental backup and migration workflows.

---

**Status:** Draft — Awaiting user feedback/refinement.
