# Requirement Proposal: `-c` Option for YAML Configuration

## Title
Add `-c`/`--config` Option: Simplified Tool Usage via YAML Configuration File

## Status
Draft

## Date
2025-07-17

## Authors
Agent

## Motivation
Currently, users must specify multiple command-line arguments to operate the file copy tool, which can be error-prone and repetitive. A configuration file (YAML) will allow users to define all options and parameters in one place, simplifying usage, improving reproducibility, and supporting more complex workflows.

## Requirements

- Add a `-c <config.yaml>` or `--config <config.yaml>` option to the CLI.
- When specified, the tool will read all operational parameters (source, destination, options, etc.) from the YAML file.
- All existing CLI options must be supported as YAML keys.
- If both CLI options and a config file are provided, CLI options override YAML values.
- The YAML file must support:
  - Source and destination paths
  - Exclusion/inclusion patterns
  - Copy/verify/summary modes
  - Any other advanced options currently supported by the CLI
- Provide a sample YAML config in the documentation.
- Update CLI help and documentation to describe the new option and YAML format.
- Add tests to ensure correct parsing and precedence of config vs CLI options.

## Constraints

- Backward compatibility: The tool must work as before if `-c` is not specified.
- The YAML parser must be robust and fail gracefully with clear error messages for invalid configs.
- The feature must be cross-platform (Windows/Linux).

## Acceptance Criteria

- Users can run the tool with `-c config.yaml` and have all options loaded from the file.
- CLI options override YAML config values.
- Documentation and help output are updated.
- Tests cover config parsing, precedence, and error handling.
