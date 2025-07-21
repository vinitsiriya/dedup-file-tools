# CLI Strategy: dedup_file_tools_compare

## Overview
This document defines the command-line interface (CLI) strategy for the `dedup_file_tools_compare` module, inspired by the conventions and usability of `dedup_file_tools_fs_copy`.

## Usage
```
python -m dedup_file_tools_compare.cli <command> [OPTIONS]
```
Or, if installed as a package:
```
dedup-file-compare <command> [OPTIONS]
```

## Global Options
- `-c`, `--config FILE`: Path to YAML configuration file (all options can be set in YAML; CLI args override YAML values)
- `--log-level LEVEL`: Set logging verbosity (default: WARNING)

## Commands and Arguments

### `init`
Initialize a new comparison job (creates `<compare-job>.db`).
- `--job-dir PATH` (required): Path to comparison job directory
- `--job-name NAME` (required): Name of the comparison job

### `add-to-left`
Add files from a directory to the left pool.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--dir PATH` (required): Directory to add to left pool

### `add-to-right`
Add files from a directory to the right pool.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--dir PATH` (required): Directory to add to right pool


### `find-missing-files`
Find files missing from one or both sides by comparing left and right pools.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--by {checksum|size|mtime|all}`: Comparison method (default: checksum)
- `--threads N`: Number of threads for parallel operations (default: 4)
- `--no-progress`: Disable progress bars
- `--left`: Show files missing from the left (present in right, not in left)
- `--right`: Show files missing from the right (present in left, not in right)
- `--both`: Show files missing from either side (union of left and right missing)


### `show-result`
Show or export the comparison results, with flexible reporting options.
- `--job-dir PATH` (required)
- `--job-name NAME` (required)
- `--summary`: Show a concise summary (counts of identical, different, missing, etc.)
- `--full-report`: Show or export the full detailed report (default if neither is specified)
- `--output FILE`: Output results to specified file (CSV or JSON). If not provided, generate the file in the job directory at a standard location (e.g., `<job-dir>/<job-name>-report.csv` or `.json`).
- `--show {identical|different|unique-left|unique-right|all}`: What to show (default: all)

## Example CLI Usage
```
# Initialize a new comparison job
dedup-file-compare init --job-dir jobs/compare1 --job-name compare1

# Add files to left and right pools
dedup-file-compare add-to-left --job-dir jobs/compare1 --job-name compare1 --dir /data/backup1
dedup-file-compare add-to-right --job-dir jobs/compare1 --job-name compare1 --dir /data/backup2


# Find files missing from the right (present in left, not in right)
dedup-file-compare find-missing-files --job-dir jobs/compare1 --job-name compare1 --right

# Find files missing from the left (present in right, not in left)
dedup-file-compare find-missing-files --job-dir jobs/compare1 --job-name compare1 --left

# Find files missing from either side
dedup-file-compare find-missing-files --job-dir jobs/compare1 --job-name compare1 --both


# Show a summary in the terminal
dedup-file-compare show-result --job-dir jobs/compare1 --job-name compare1 --summary

# Show or export the full report to a specific file
dedup-file-compare show-result --job-dir jobs/compare1 --job-name compare1 --full-report --output diff.csv --show different

# If --output is not specified, the report is generated in the job directory automatically
dedup-file-compare show-result --job-dir jobs/compare1 --job-name compare1 --full-report
```

## Notes

- The CLI is designed for clarity, scriptability, and consistency with other tools in the project.
- All commands and options are discoverable via `-h` or `--help`.
- YAML config support allows for easy automation and reproducibility.
- The `find-missing-files` command replaces the previous `compare` command and provides focused options for missing file detection on either or both sides.
- The `show-result` command now supports `--summary` for quick overviews and `--full-report` for detailed output. If `--output` is not specified, reports are saved in the job directory by default.

## Suggestions for Improving Results Reporting

+- Add support for filtering and sorting results (e.g., by file size, path, or type of difference).
+- Allow output in CSV and JSON formats only (keep feature set minimal).
+- Provide a machine-readable summary (e.g., JSON with counts and key stats) for automation.
+- Support diff-friendly output for easy comparison with previous runs.
+- Include timestamps and job metadata in reports for traceability.
+- Allow users to select columns/fields to include in the report.
