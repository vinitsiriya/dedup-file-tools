# Standalone Documentation: Directory Compare Tool (dedup_file_tools_compare)

## Table of Contents
1. [Overview](#overview)
2. [Protocol Compliance](#protocol-compliance)
3. [CLI Automation & YAML Config Usage](#cli-automation--yaml-config-usage)
4. [Log & CSV Parsing, Audit Trails](#log--csv-parsing-audit-trails)
5. [Example Agent Workflow](#example-agent-workflow)
6. [Error Handling, Reproducibility, and Protocol Compliance](#error-handling-reproducibility-and-protocol-compliance)
7. [Full CLI Reference](#full-cli-reference)
8. [References](#references)

---

## 1. Overview
The `dedup_file_tools_compare` module provides a robust, scriptable command-line tool to compare two directories by checksum, size, or modification time. It is designed for backup verification, migration audits, and large-scale file integrity checks. Results are stored in a persistent SQLite database and can be exported as CSV or JSON for further analysis.

## 2. Protocol Compliance
- Follows strict, phase-based workflow: init, add-to-left, add-to-right, find-missing-files, show-result
- All actions are logged and auditable
- Output and logs are deterministic and reproducible
- CLI and output formats are stable for automation

## 3. CLI Automation & YAML Config Usage
- All phases can be scripted via CLI for batch or CI workflows
- Supports YAML config for job parameters (planned/roadmap)
- Example CLI automation:
  ```sh
  dedup-file-compare init --job-dir jobs/compare1 --job-name myjob
  dedup-file-compare add-to-left --job-dir jobs/compare1 --job-name myjob --dir /data/source
  dedup-file-compare add-to-right --job-dir jobs/compare1 --job-name myjob --dir /data/backup
  dedup-file-compare find-missing-files --job-dir jobs/compare1 --job-name myjob
  dedup-file-compare show-result --job-dir jobs/compare1 --job-name myjob --output results.csv
  ```

## 4. Log & CSV Parsing, Audit Trails
- All actions and results are logged to the job's SQLite DB
- CSV/JSON output for integration with external tools
- Logs include phase timings, errors, and file-level details
- Designed for auditability and compliance

## 5. Example Agent Workflow
1. Initialize job
2. Add left/right directories
3. Run comparison (find-missing-files)
4. Export and parse results (CSV/JSON)
5. Use logs for audit or troubleshooting

## 6. Error Handling, Reproducibility, and Protocol Compliance
- All errors are logged with context
- CLI returns nonzero exit code on failure
- Results are reproducible given the same inputs
- Protocol steps must be followed in order; tool enforces phase sequence

## 7. Full CLI Reference

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

## 8. References
- [Developer Requirements](../requirements/requirements.md)
- [Implementation Details](../implementation/find-missing-files-checksum.md)
- [Feature Overview](../feature/find-missing-files-checksum.md)
- [User Perspective](../user_prepective/README.md)

---
For support, bug reports, or feature requests, see the project repository.
