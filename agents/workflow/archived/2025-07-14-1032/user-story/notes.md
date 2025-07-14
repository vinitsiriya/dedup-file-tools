# Notes: Import Checksum Cache Table

- The cache table should never overwrite trusted or computed checksums in the main tables.
- Consider performance implications for large datasets when using the cache as a fallback.
- Ensure all cache imports are logged with source and timestamp for auditability.
- User communication is critical: CLI warnings, docs, and migration guides must be clear.
- Test for edge cases where both main and cache checksums are missing or disagree.

---

*Created: 2025-07-14*
*Author: Agent (GitHub Copilot)*
