# CLI Reference: dedup_file_tools_dupes_move

This document describes the command-line interface for the deduplication/removal tool, following the documentation agent protocol.

## Usage

```
python -m dedup_file_tools_dupes_move.main [PHASE] [OPTIONS]
```

## Phases

- `init`: Initialize a new deduplication job
- `analyze`: Scan lookup pool, compute checksums, group duplicates
- `move`: Move/remove duplicates to dupes folder
- `verify`: Check that moves/removals were successful
- `summary`: Print summary and generate CSV report
- `one-shot`: Run the full deduplication workflow in one command

## Common Options

- `--job-dir PATH`: Job directory (required)
- `--job-name NAME`: Job name (required)
- `--lookup-pool PATH`: Source folder for scanning
- `--dupes-folder PATH`: Destination/removal folder
- `--threads N`: Number of threads (default: 4)
- `--log-level LEVEL`: Set logging verbosity (info, debug, etc.)
- `--config FILE`: YAML config file (optional)
- `--help`: Show help for any phase or the main CLI

## Example

```
python -m dedup_file_tools_dupes_move.main one-shot --job-dir ./jobs --job-name myjob --lookup-pool ./data --dupes-folder ./dupes
```

---

See feature/dupes_move.md and implementation/dupes_move.md for details.
