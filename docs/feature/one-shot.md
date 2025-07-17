# Feature: One-Shot Command

## Summary
The one-shot command allows users to run the entire file copy workflow in a single CLI command, with robust error handling and all relevant options.

## Usage
```
python -m fs_copy_tool.main one-shot --job-dir <job-dir> --job-name <job-name> --src <SRC_ROOT> --dst <DST_ROOT> [options]
```

- Runs: init, import, add-source, add-to-destination-index-pool, analyze, checksum, copy, verify, summary
- Stops immediately if any step fails and prints an error
- Prints "Done" on success

### Options
- `--threads`, `--no-progress`, `--log-level`, `--resume`, `--reverify`, `--checksum-db`, `--other-db`, `--table`, `--stage`, `--skip-verify`

## Example
```
python -m fs_copy_tool.main one-shot --job-dir jobs/job1 --job-name job1 --src /mnt/src --dst /mnt/dst --threads 4 --log-level DEBUG
```

## Notes
- See CLI documentation for all options and details.
- See requirements and implementation docs for technical details.
