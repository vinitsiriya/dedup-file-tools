# Robust SQLite Refactor Plan and Progress

## Goal
Refactor all direct SQLite connection usage in the codebase to use a single robust utility (`RobustSqliteConn`) for WAL mode, timeouts, and retry logic, to eliminate `database is locked` errors and improve concurrency.

## Steps

1. **Create Utility**
   - [x] Implemented `RobustSqliteConn` in `fs_copy_tool/utils/robust_sqlite.py`.

2. **Inventory All Usages**
   - [x] Searched for all `sqlite3.connect` usages in codebase.
   - [x] Identified all files and functions needing refactor.

3. **Refactor Main Modules**
   - [ ] `main.py`: Replace all `sqlite3.connect` with `RobustSqliteConn`.
   - [ ] `db.py`: Use utility for schema/init.
   - [ ] `phases/copy.py`, `phases/verify.py`, `phases/summary.py`, `phases/analysis.py`: Refactor all DB access.
   - [ ] `utils/checksum_cache.py`, `utils/destination_pool.py`: Refactor to use utility.

4. **Test and Validate**
   - [ ] Run all tests and large jobs to confirm no locking errors.
   - [ ] Adjust retry/timeouts as needed.

5. **Document**
   - [x] This plan and progress file.
   - [ ] Update developer docs if needed.

## Notes
- All connection logic will be single-sourced for easier tuning and reliability.
- WAL mode and timeouts will be default for all DB access.
- If any module needs custom retry/timeout, utility supports override.

## Progress Log
- 2025-07-17: Utility created, inventory complete, starting main.py refactor.

---

*Update this file as you progress with each module.*
