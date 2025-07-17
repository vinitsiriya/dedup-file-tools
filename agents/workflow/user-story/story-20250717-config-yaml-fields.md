# User Story: YAML Configuration Option (`-c`)

## Title
As a user, I want to provide all tool options in a YAML configuration file using the `-c` flag, so that I can simplify and automate my file copy workflows.

## Status
Draft

## Date
2025-07-17

## Authors
Agent

## Context
Currently, users must specify all options via the command line, which is repetitive and error-prone for complex jobs. A YAML config file will allow users to save, reuse, and share configurations easily. The YAML file should support all CLI options, and CLI arguments should override YAML values if both are provided.

## Story
As a user of the file copy tool,
I want to specify a configuration file with `-c config.yaml`,
So that all my source, destination, and advanced options are loaded automatically,
And I can override any value with a CLI argument if needed.

## Acceptance Criteria
- I can run the tool with `-c config.yaml` and have all options loaded from the file.
- All CLI options are supported as YAML keys.
- CLI arguments override YAML config values.
- The tool provides clear errors for invalid YAML or missing required fields.
- Documentation includes a sample YAML config and usage instructions.
- Tests verify config parsing, precedence, and error handling.
- All fields listed in the YAML configuration plan are supported.

## Notes
- The feature must be cross-platform.
- Backward compatibility is required: the tool works as before if `-c` is not used.
- The YAML config must support all commands and options as described in the field mapping table.
