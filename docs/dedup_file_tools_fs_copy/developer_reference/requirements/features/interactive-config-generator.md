# Requirements: Interactive Config Generator

## Summary
Add an interactive CLI feature to generate a YAML config file for the file-copy tool. The tool will prompt the user for required settings step-by-step and output a config file compatible with the `-c` option.

## Requirements
- Add a CLI command `generate-config` to start the interactive config generator.
- Prompt for all required config fields, with descriptions and defaults.
- Validate user input and allow skipping optional fields.
- Display a summary and ask for confirmation before writing.
- Write a valid YAML config file for use with `-c`.
- Must be robust, user-friendly, and not break existing CLI workflows.
- Documentation must be updated to describe the new feature and its usage.

## Out of Scope
- No changes to the config file format itself.
- No GUI or web-based config generation (CLI only).

## Acceptance Criteria
- Users can run the interactive config generator from the CLI.
- The tool guides the user through all required fields and writes a valid YAML config file.
- The generated config works seamlessly with the existing `-c` option.
- Documentation is updated.
