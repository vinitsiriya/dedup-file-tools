# User Story: As a user, I want global duplicate detection using a destination index pool

## Story

As a user, I want the file copy tool to avoid copying files that already exist anywhere in my destination pool (not just at the target path), so that I can prevent unnecessary duplicates and save storage space. The destination index pool is a separate index and must not be confused with the main job/copy database. All duplicate detection and indexing must be performed according to the canonical uidpath abstraction, not just raw filesystem paths. I want to be able to update and maintain this index pool efficiently, and choose between path-specific and pool-wide duplicate detection as needed.

---

## Acceptance Criteria
- I can run a CLI command to scan and add files to the destination index pool.
- The tool can check for duplicates across the entire destination pool before copying.
- The index pool is updated efficiently and is safe to update multiple times.
- I can refresh the index pool checksums as a separate phase.
- I can configure the duplicate detection mode (path-specific or pool-wide).

_Proposed: 2025-07-15_
_Author: GitHub Copilot_
