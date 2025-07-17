# User Story: Interactive Config Generator

## Title
As a user, I want to generate a YAML config file interactively via the CLI so that I can easily set up the tool without manual editing or guesswork.

## Narrative
- As a new or existing user,
- I want to run `python -m fs_copy_tool generate-config`,
- So that the tool will ask me questions about all required settings,
- And write a valid YAML config file for me to use with the `-c` option.

## Acceptance Criteria
- [ ] A new CLI command `generate-config` is available.
- [ ] The command launches an interactive prompt, asking for all required config fields.
- [ ] The tool validates input and provides helpful descriptions and defaults.
- [ ] The user can skip optional fields or accept defaults.
- [ ] At the end, the tool summarizes the config and asks for confirmation before writing.
- [ ] The config is saved as a valid YAML file, ready for use with the tool.
- [ ] Documentation is updated to describe this workflow.

## Notes
- The process should be user-friendly and robust against invalid input.
- The generated config must be compatible with the existing `-c` option.

---

*Status: Draft. Please review or suggest edits before marking as ready for tasks.*
