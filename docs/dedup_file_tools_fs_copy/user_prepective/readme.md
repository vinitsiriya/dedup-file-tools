
# Non-Redundant Media File Copy Tool: User Guide

Welcome! This guide will help you get started with dedup_file_tools_fs_copy, a robust, resumable, and auditable file copy tool for safe, non-redundant media migration between storage pools.

## What is this tool?
This tool copies files from one or more source folders to one or more destination folders, ensuring no duplicate files are copied. All actions are tracked in a job-specific database for full traceability and resumability. The tool supports both fixed and removable drives, and is designed for robust, auditable workflows.

---

# Tutorial: Step-by-Step Example

Let's walk through a typical workflow using the tool. This tutorial assumes you have Python and the tool installed.

### 1. Install the tool
```
pip install .
```
Or, for isolated CLI usage:
```
pipx install .
```

### 2. Generate a config file (recommended)
Run the interactive config generator:
```
python fs_copy_tool/main.py generate-config
```
Follow the prompts to create a `config.yaml` file with your job directory, job name, source(s), and destination(s).

### 3. Initialize a job (optional if using one-shot)
If you want to set up the job directory manually:
```
python fs_copy_tool/main.py init --job-dir ./myjob --job-name myjob
```

### 4. Analyze your files
Scan your source and destination for files:
```
python fs_copy_tool/main.py analyze --job-dir ./myjob --job-name myjob --src ./source --dst ./dest
```

### 5. Compute checksums
Calculate checksums for all source files:
```
python fs_copy_tool/main.py checksum --job-dir ./myjob --job-name myjob --table source_files --threads 8
```

### 6. Copy files
Copy all non-duplicate files from source to destination:
```
python fs_copy_tool/main.py copy --job-dir ./myjob --job-name myjob --src ./source --dst ./dest --threads 8
```

### 7. Verify the copy
Check that all files were copied correctly (shallow verification):
```
python fs_copy_tool/main.py verify --job-dir ./myjob --job-name myjob --src ./source --dst ./dest --stage shallow
```
For deep (checksum) verification:
```
python fs_copy_tool/main.py verify --job-dir ./myjob --job-name myjob --src ./source --dst ./dest --stage deep
```

### 8. View job status and logs
Check progress and see the audit trail:
```
python fs_copy_tool/main.py status --job-dir ./myjob --job-name myjob
python fs_copy_tool/main.py log --job-dir ./myjob --job-name myjob
```

### 9. Run the full workflow in one step (one-shot)
You can run all steps above in a single command:
```
python fs_copy_tool/main.py one-shot -c config.yaml
```

---
## CLI Command Quick Reference

| Command | Purpose | Key Arguments |
|---------|---------|--------------|
| generate-config | Interactively create a YAML config file | - |
| init | Initialize a new job directory | --job-dir, --job-name |
| import-checksums | Import checksums from another job | --job-dir, --job-name, --other-db |
| analyze | Analyze source/destination for files | --job-dir, --job-name, --src, --dst |
| checksum | Compute/update checksums | --job-dir, --job-name, --table, --threads |
| copy | Copy files, skipping duplicates | --job-dir, --job-name, --src, --dst, --threads |
| resume | Resume interrupted copy jobs | --job-dir, --job-name, --src, --dst, --threads |
| status | Show job progress and stats | --job-dir, --job-name |
| log | Show job log/audit trail | --job-dir, --job-name |
| verify | Verify copied files (shallow/deep) | --job-dir, --job-name, --src, --dst, --stage |
| deep-verify | Deep checksum verification | --job-dir, --job-name, --src, --dst |
| verify-status, deep-verify-status, ... | Show verification results/summaries | --job-dir, --job-name |
| add-file | Add a single file to the job | --job-dir, --job-name, --file |
| add-source | Add a source directory | --job-dir, --job-name, --src |
| list-files | List all files in the job | --job-dir, --job-name |
| remove-file | Remove a file from the job | --job-dir, --job-name, --file |
| one-shot | Run the full workflow in one command | --job-dir, --job-name, --src, --dst, --threads |
| add-to-destination-index-pool | Update destination pool index | --job-dir, --job-name, --dst |






---


## YAML Config Support
You can use a YAML config file for reproducible runs:
```
python fs_copy_tool/main.py one-shot -c config.yaml
```
Command-line arguments always override config values.

---


## About UidPath: Robust, Portable File Tracking
This tool uses a system-independent path abstraction called **UidPath**. Instead of relying on drive letters (which can change, especially on Windows), UidPath uses a unique identifier (UID) for each filesystem and stores file paths relative to the mount point. This means:
- Your checksum cache and job database remain valid even if drive letters or mount points change.
- The tool is robust to moving drives between systems or plugging them into different USB ports.
- Copy, deduplication, and verification work reliably across different environments.
For more details, see the [UidPath documentation](../../dedup_file_tools_commons/uidpath.md).

## Troubleshooting & Tips
- All logs and job state are stored in your job directory.
- If a command fails, check the logs in the job directory for details.
- You can safely re-run any phase; the tool is idempotent and will not repeat completed work.
- Use more threads for faster processing on large datasets.
- The tool never deletes files from your original data folder unless you explicitly copy them to a destination.
- If you omit optional arguments, the tool will use values from your config file or prompt as needed.

---


## More Help
- For full CLI reference and advanced usage, see the developer documentation in `docs/dedup_file_tools_fs_copy/developer_reference/cli.md`.
- For protocol and agent integration, see `docs/dedup_file_tools_fs_copy/standalone/external_ai_tool_doc.md`.

---

Happy copying!
