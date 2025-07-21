# CLI Usage: dedup_file_tools_compare

## Commands

- `init` — Initialize a new comparison job
  - `--job-dir` DIR
  - `--job-name` NAME
- `add-to-left` — Add files from a directory to the left pool
  - `--job-dir` DIR
  - `--job-name` NAME
  - `--dir` DIR
- `add-to-right` — Add files from a directory to the right pool
  - `--job-dir` DIR
  - `--job-name` NAME
  - `--dir` DIR
- `find-missing-files` — Find files missing from one or both sides
  - `--job-dir` DIR
  - `--job-name` NAME
  - `--by` [checksum|size|mtime|all] (default: checksum)
  - `--threads` N (default: 4)
  - `--no-progress`
  - `--left` / `--right` / `--both`
- `show-result` — Show or export the comparison results
  - `--job-dir` DIR
  - `--job-name` NAME
  - `--summary`
  - `--full-report`
  - `--output` FILE (CSV or JSON)
  - `--show` [identical|different|unique-left|unique-right|all] (default: all)

## Example Workflow

```sh
# Initialize job
dedup-file-compare init --job-dir jobs/compare1 --job-name myjob
# Add files to left and right pools
dedup-file-compare add-to-left --job-dir jobs/compare1 --job-name myjob --dir /data/source
dedup-file-compare add-to-right --job-dir jobs/compare1 --job-name myjob --dir /data/backup
# Find missing files
dedup-file-compare find-missing-files --job-dir jobs/compare1 --job-name myjob
# Show results in summary
dedup-file-compare show-result --job-dir jobs/compare1 --job-name myjob --summary
# Export results to CSV
dedup-file-compare show-result --job-dir jobs/compare1 --job-name myjob --output results.csv
```

## Output
- Console summary, full report, CSV, or JSON.
- All results are also stored in the job's SQLite DB for scripting and audit.
