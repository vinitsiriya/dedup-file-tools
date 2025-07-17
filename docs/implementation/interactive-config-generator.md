# Implementation: Interactive Config Generator

## Overview
Implements a new CLI command `generate-config` that interactively prompts the user for all required configuration fields and writes a valid YAML config file for use with the `-c` option.

## Details
- Adds a new command to the CLI parser: `generate-config`.
- When invoked, the tool prompts the user for each required field (job_dir, job_name, src, dst, threads, log_level, etc.).
- Input is validated and defaults are provided where appropriate.
- At the end, a summary is shown and the user is asked to confirm before writing the file.
- The config is written as a YAML file, ready for use with any command supporting `-c`.
- The implementation is modular and does not affect existing CLI workflows.
- Tests are included to verify the feature.

## Key Functions
- `interactive_config_generator()` in `fs_copy_tool/utils/interactive_config.py`
- CLI integration in `fs_copy_tool/main.py`

## Test Coverage
- Automated test simulates user input and verifies the generated YAML file.

## Notes
- No changes to the config file format or other CLI commands.
- No GUI or web-based interface.
