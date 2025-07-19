
# Feature: One-Shot Command

## Summary
The `one-shot` command runs the entire file copy and verification workflow in a single CLI invocation. It automates all phases, provides robust error handling, and supports YAML config files for simplified usage.

## Workflow Steps (in order)
1. **Init**: Initialize the job directory and database.
2. **Import Checksums** (optional): Import checksums from another compatible job database if `--other-db` is provided.
3. **Add Source**: Register the source directory.
4. **Add to Destination Index Pool**: Register the destination directory or pool using `--dst-index-pool` (or `--destination-index-pool`). This step is required for workflows that use a destination index pool for deduplication or multi-destination management. If not provided, the first `--dst` value is used as the pool by default.
5. **Analyze**: Scan source and destination for file metadata.
6. **Checksums (source)**: Compute or update checksums for all source files.
7. **Checksums (destination)**: Compute or update checksums for all destination files.
8. **Copy**: Copy files from source to destination, skipping duplicates and resuming incomplete jobs if needed.
9. **Verify (shallow)**: Verify copied files by size and timestamp (skipped if `--skip-verify`).
10. **Verify (deep)**: Optionally verify files by checksum if `--deep-verify` or `--stage deep` is specified.
11. **Summary**: Print a summary of the job results.

If any step fails, the workflow stops immediately and prints an error message. On success, prints `Done`.

## Usage
```
python -m fs_copy_tool.main one-shot --job-dir <job-dir> --job-name <job-name> --src <SRC_ROOT> --dst <DST_ROOT> [options]
```
Or, using a YAML config file:
```
python -m fs_copy_tool.main one-shot -c config.yaml
```
Command-line arguments always override YAML config values.


## Key Options
- `-c <config.yaml>`, `--config <config.yaml>`: Load all options from a YAML config file (see `generate-config` command).
- `--job-dir <path>`: Directory for job state and database.
- `--job-name <name>`: Name for this job.
- `--src <SRC_ROOT>`: Source directory (can be specified multiple times for multiple sources).
- `--dst <DST_ROOT>`: Destination directory (can be specified multiple times).
- `--dst-index-pool <POOL_PATH>`, `--destination-index-pool <POOL_PATH>`: Specify a destination index pool for deduplication or multi-destination workflows. This is used in the "Add to Destination Index Pool" step. If not provided, the first `--dst` value is used as the pool by default.
- `--threads N`: Number of threads for parallel operations (default: 4).
- `--no-progress`: Disable progress bars.
- `--log-level LEVEL`: Set logging level (default: INFO).
- `--resume`: Resume incomplete jobs (default: True for copy phase).
- `--reverify`: Force re-verification in verify/deep-verify.
- `--checksum-db <path>`: Custom checksum DB path.
- `--other-db <path>`: Import checksums from another compatible SQLite database.
- `--skip-verify`: Skip all verification steps.
- `--deep-verify`: Perform deep (checksum) verification after copy.
- `--stage <shallow|deep>`: Control verification stage (default: shallow).

See the [CLI documentation](../cli.md) for a full list of options and details.


## Example
```
python -m fs_copy_tool.main one-shot --job-dir jobs/job1 --job-name job1 --src /mnt/src --dst /mnt/dst --dst-index-pool /mnt/pool --threads 4 --log-level DEBUG
```
Or, with a YAML config:
```
python -m fs_copy_tool.main one-shot -c config.yaml --dst-index-pool /mnt/pool --threads 8
```
If `--dst-index-pool` is not specified, the first `--dst` value is used as the pool by default.

## Error Handling
- If any step fails, the workflow stops and prints an error message for that step.
- No further steps are executed after a failure.
- On success, prints `Done`.

## Notes
- Use `generate-config` to create a YAML config interactively.
- All workflow steps are auditable and resumable.
- For technical details, see requirements and implementation docs.
