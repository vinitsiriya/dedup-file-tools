# Interactive Config Generator

This module provides an interactive CLI for generating a YAML config file for the file-copy tool. It is invoked via:

    python -m fs_copy_tool generate-config

The user is prompted for all required fields, and the resulting config is saved as a YAML file compatible with the -c option.

---

## Usage
- Run `python -m fs_copy_tool generate-config` to start the interactive prompt.
- Answer the questions for each required field.
- Review the summary and confirm to write the config file.
- Use the generated YAML file with the `-c` option in future runs.

---

*Last updated: 2025-07-18*
