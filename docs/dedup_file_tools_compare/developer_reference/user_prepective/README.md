# User Perspective: Directory Compare Tool (dedup-file-compare)

## Overview
The `dedup-file-compare` tool provides a robust, scriptable command-line interface to compare two directories by checksum. It is designed for users who need to verify, audit, or synchronize large file sets, such as backups or data migrations.

## Key Features
- Compare two directories by file checksum (default), size, or modification time
- Identify files unique to either side, or present in both
- Fast, parallelized checksum calculation with persistent caching
- Output results as console summary, full report, CSV, or JSON
- All results are stored in a persistent SQLite database for scripting and audit
- Modular, phase-based workflow for advanced scripting

## Typical Use Cases
- Verifying backup integrity
- Auditing file transfers or migrations
- Finding missing or extra files between two locations
- Generating reports for compliance or troubleshooting

## Example Workflow
1. **Initialize a comparison job:**
   ```sh
   dedup-file-compare init --job-dir jobs/compare1 --job-name myjob
   ```
2. **Add files to left and right pools:**
   ```sh
   dedup-file-compare add-to-left --job-dir jobs/compare1 --job-name myjob --dir /data/source
   dedup-file-compare add-to-right --job-dir jobs/compare1 --job-name myjob --dir /data/backup
   ```
3. **Find missing files:**
   ```sh
   dedup-file-compare find-missing-files --job-dir jobs/compare1 --job-name myjob
   ```
4. **Show results in summary or export to CSV:**
   ```sh
   dedup-file-compare show-result --job-dir jobs/compare1 --job-name myjob --summary
   dedup-file-compare show-result --job-dir jobs/compare1 --job-name myjob --output results.csv
   ```

## Output
- Console summary: quick overview of identical, different, unique files
- Full report: detailed per-file comparison
- CSV/JSON: for further analysis or scripting
- When using `--output` for CSV, results are written as separate files (`missing_left.csv`, `missing_right.csv`, `identical.csv`, `different.csv`) in a timestamped `reports_YYYYMMDD_HHMMSS` directory under the job directory.
- All results are stored in the job's SQLite DB

## Advanced Usage
- Use `--by size` or `--by mtime` for alternative comparison modes
- Use `--threads N` to control parallelism
- Use `--no-progress` for scripting or automation
- Filter results with `--show` (identical, different, unique-left, unique-right, all)

## See Also
- [CLI Reference](cli.md) for full command and option details
- [Developer Reference](../requirements/requirements.md) for technical details

---
For support or bug reports, see the project repository.
