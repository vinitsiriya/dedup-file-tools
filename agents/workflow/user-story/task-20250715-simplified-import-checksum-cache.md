# Task List: Simplified and Standardized Checksum Import

## Audit and Implementation Tasks

- [ ] Audit `main.py` and all CLI logic to ensure only `checksum_cache` import is supported
- [ ] Remove legacy import logic for `source_files` and `destination_files`
- [ ] Change CLI argument from `--old-db` to `--other-db` in all code, help text, and documentation
- [ ] Update argument parsing and handler logic to only allow import from `checksum_cache`
- [ ] Add schema validation for the `checksum_cache` table in the other database
- [ ] Update CLI help text and documentation to reflect the new, single import path
- [ ] Remove or update any tests or docs referencing legacy import options
- [ ] Test the new import logic for compatibility, robustness, and error handling
- [ ] Update user and developer documentation to match the new behavior
- [ ] Mark this user story and requirement as complete and archive when done

---

Linked user story: story-20250715-simplified-import-checksum-cache.md
Linked requirement: requirement-20250715-simplified-import-checksum-cache.md
