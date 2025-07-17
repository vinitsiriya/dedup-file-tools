# Requirement Proposal: Interactive Config Generator

## Summary
Add an interactive CLI feature to generate a YAML config file for the file-copy tool. The tool will prompt the user for required settings step-by-step and output a config file compatible with the `-c` option.

## Motivation
- Simplifies onboarding for new users.
- Reduces manual errors in config creation.
- Ensures all required fields are captured in a user-friendly way.

## Requirements
- Add a CLI command or option (e.g., `generate-config` or `--interactive-config`) to start the interactive config generator.
- The generator will:
  - Prompt the user for all required config fields (with descriptions and defaults where appropriate).
  - Validate user input for each field.
  - Allow the user to skip optional fields or accept defaults.
  - At the end, display a summary and ask for confirmation before writing the file.
  - Write the config as a valid YAML file, ready for use with the `-c` option.
- The feature must be robust, user-friendly, and not break existing CLI workflows.
- Documentation must be updated to describe the new feature and its usage.

## Out of Scope
- No changes to the config file format itself.
- No GUI or web-based config generation (CLI only).

## Acceptance Criteria
- Users can run the interactive config generator from the CLI.
- The tool guides the user through all required fields and writes a valid YAML config file.
- The generated config works seamlessly with the existing `-c` option.
- Documentation is updated.

---

*Status: Draft. Please review and suggest refinements or approve to proceed.*
