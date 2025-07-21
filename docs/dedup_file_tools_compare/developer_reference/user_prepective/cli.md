
# CLI Usage: dedup-file-compare

## Global Options
- `--config` YAML config file
- `--log-level` Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file` Custom log file path (default: job logs dir)

## Commands & Options

### `init`
Initialize a new comparison job.
- `--job-dir` DIR (required)
- `--job-name` NAME (required)

### `add-to-left`
Add files from a directory to the left pool.
- `--job-dir` DIR (required)
- `--job-name` NAME (required)
- `--dir` DIR (required)

### `add-to-right`
Add files from a directory to the right pool.
- `--job-dir` DIR (required)
- `--job-name` NAME (required)
- `--dir` DIR (required)

### `find-missing-files`
Find files missing from one or both sides (always compares by checksum).
- `--job-dir` DIR (required)
- `--job-name` NAME (required)
- `--threads` N (default: 4)
- `--no-progress` (flag)
- `--left` (flag)
- `--right` (flag)
- `--both` (flag)

### `show-result`
Show or export the comparison results.
- `--job-dir` DIR (required)
- `--job-name` NAME (required)
- `--summary` (flag)
- `--full-report` (flag)
- `--output` FILE (CSV or JSON; if CSV, will create a timestamped reports directory with multiple CSVs)
- `--show` [identical|different|unique-left|unique-right|all] (default: all)
- `--use-normal-paths` (flag; output absolute paths in the report)

### `one-shot`
Run the full workflow (init, add-to-left, add-to-right, find-missing-files, show-result) in one command (always compares by checksum).
- `--job-dir` DIR (required)
- `--job-name` NAME (required)
- `--left` DIR (required)
- `--right` DIR (required)
- `--threads` N (default: 4)
- `--no-progress` (flag)
- `--output` FILE (CSV or JSON)
- `--show` [identical|different|unique-left|unique-right|all] (default: all)
- `--summary` (flag)
- `--full-report` (flag)
- `--use-normal-paths` (flag)

### `import-checksums`
Import checksums from the checksum_cache table of another compatible database.
- `--job-dir` DIR (required)
- `--job-name` NAME (required)
- `--other-db` PATH (required)

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
# Export results to CSV (creates reports_YYYYMMDD_HHMMSS/ with multiple CSVs)
dedup-file-compare show-result --job-dir jobs/compare1 --job-name myjob --output results.csv
```

## Output
- Console summary, full report, CSV, or JSON.
- When using `--output` for CSV, results are written as separate files (`missing_left.csv`, `missing_right.csv`, `identical.csv`, `different.csv`) in a timestamped `reports_YYYYMMDD_HHMMSS` directory under the job directory.
- All results are also stored in the job's SQLite DB for scripting and audit.
