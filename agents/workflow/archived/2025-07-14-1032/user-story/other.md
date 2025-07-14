# Other Artifacts: Import Checksum Cache Table

- Example schema for `checksum_cache`:

  ```sql
  CREATE TABLE IF NOT EXISTS checksum_cache (
      uid TEXT,
      relative_path TEXT,
      checksum TEXT,
      source TEXT,
      imported_at INTEGER,
      PRIMARY KEY (uid, relative_path, source)
  );
  ```

- Example CLI usage:
  ```sh
  python -m fs_copy_tool.main import-checksums --job-dir .copy-task --old-db old.db --cache
  ```

- Example migration script snippet:
  ```python
  # Copy from cache to main table if missing
  cur.execute('''
      INSERT OR IGNORE INTO source_files (uid, relative_path, checksum)
      SELECT uid, relative_path, checksum FROM checksum_cache
      WHERE NOT EXISTS (
          SELECT 1 FROM source_files WHERE source_files.uid = checksum_cache.uid AND source_files.relative_path = checksum_cache.relative_path AND source_files.checksum IS NOT NULL
      )
  ''')
  ```

---

*Created: 2025-07-14*
*Author: Agent (GitHub Copilot)*
