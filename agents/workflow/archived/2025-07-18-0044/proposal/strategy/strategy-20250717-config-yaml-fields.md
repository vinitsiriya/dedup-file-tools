# YAML Configuration Plan for `-c` Option

## Supported Top-Level Fields

- `command`: (string, required)
  The main command to run. One of: `one-shot`, `init`, `import-checksums`, `analyze`, `checksum`, `copy`, `resume`, `status`, `log`, `verify`, `deep-verify`, `verify-status`, `deep-verify-status`, `add-file`, `add-source`, `list-files`, `remove-file`, `summary`, `add-to-destination-index-pool`.

- `job_dir`: (string, required for most commands)
  Path to the job directory.

- `job_name`: (string, required for most commands)
  Name of the job (database file will be `<job_name>.db`).

- `src`: (list of strings, required for commands that operate on source volumes)
  List of source volume root directories.

- `dst`: (list of strings, required for commands that operate on destination volumes)
  List of destination volume root directories.

- `threads`: (integer, optional)
  Number of threads for parallel operations (default: 4).

- `no_progress`: (bool, optional)
  Disable progress bars.

- `log_level`: (string, optional)
  Set logging level (default: INFO).

- `resume`: (bool, optional)
  Resume incomplete jobs (default: True for copy phase).

- `reverify`: (bool, optional)
  Force re-verification in verify/deep-verify.

- `checksum_db`: (string, optional)
  Custom checksum DB path.

- `other_db`: (string, optional)
  Path to another compatible SQLite database for importing checksums.

- `table`: (string, optional)
  Table to use for checksumming (`source_files` or `destination_files`).

- `stage`: (string, optional)
  Verification stage (`shallow` or `deep`).

- `skip_verify`: (bool, optional)
  Skip verification steps.

- `deep_verify`: (bool, optional)
  Perform deep verification after shallow verification.

- `dst_index_pool`: (string, optional)
  Path to destination index pool.

- `file`: (string, for add-file/remove-file)
  Path to the file to add or remove.

## Example YAML

```yaml
command: one-shot
job_dir: /path/to/job
job_name: myjob
src:
  - /mnt/source1
  - /mnt/source2
dst:
  - /mnt/dest1
  - /mnt/dest2
threads: 8
no_progress: true
log_level: DEBUG
resume: true
reverify: false
checksum_db: /path/to/custom-checksum.db
other_db: /path/to/other-job.db
table: source_files
stage: deep
skip_verify: false
deep_verify: true
dst_index_pool: /mnt/dest1/index-pool
```

## Field Mapping Table

| YAML Key         | CLI Option/Arg           | Type      | Commands Used In                | Description                                      |
|------------------|-------------------------|-----------|----------------------------------|--------------------------------------------------|
| command          | <subcommand>            | string    | all                              | Main command to run                              |
| job_dir          | --job-dir               | string    | most                             | Path to job directory                            |
| job_name         | --job-name              | string    | most                             | Name of the job                                  |
| src              | --src                   | list      | one-shot, analyze, copy, etc.    | Source volume roots                              |
| dst              | --dst                   | list      | one-shot, analyze, copy, etc.    | Destination volume roots                         |
| threads          | --threads               | int       | one-shot, checksum, copy, etc.   | Number of threads                                |
| no_progress      | --no-progress           | bool      | one-shot, checksum, copy, etc.   | Disable progress bars                            |
| log_level        | --log-level             | string    | one-shot, all                    | Logging level                                    |
| resume           | --resume                | bool      | one-shot, copy, resume           | Resume incomplete jobs                           |
| reverify         | --reverify              | bool      | one-shot, verify, deep-verify    | Force re-verification                            |
| checksum_db      | --checksum-db           | string    | one-shot, checksum, etc.         | Custom checksum DB path                          |
| other_db         | --other-db              | string    | one-shot, import-checksums       | Import checksums from another DB                 |
| table            | --table                 | string    | one-shot, checksum               | Table for checksumming                           |
| stage            | --stage                 | string    | one-shot, verify                 | Verification stage                               |
| skip_verify      | --skip-verify           | bool      | one-shot                         | Skip verification steps                          |
| deep_verify      | --deep-verify           | bool      | one-shot                         | Perform deep verification                        |
| dst_index_pool   | --dst-index-pool        | string    | one-shot                         | Destination index pool path                      |
| file             | --file                  | string    | add-file, remove-file            | File to add/remove                               |

## Notes

- All CLI options are supported as YAML keys.
- CLI arguments override YAML config values if both are provided.
- The YAML parser must validate required fields for the selected command.
- The tool must provide clear error messages for missing or invalid fields.

---
