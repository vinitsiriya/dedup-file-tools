# Implementation: One-Shot Command

## Overview
The one-shot command is implemented as a CLI subcommand that orchestrates the entire file copy workflow in a single invocation, with robust error handling and clear user feedback.

## Key Implementation Details
- Added a `one-shot` subparser to the CLI using `argparse`.
- All required and optional arguments are supported and passed to the workflow steps.
- The workflow is implemented in `run_main_command(args)` in `fs_copy_tool/main.py`.
- Each step (init, import, add-source, etc.) is called in sequence.
- After each step, the return value is checked. If any step fails (non-zero return or exception), the workflow stops and prints an error.
- If all steps succeed, a "Done" message is printed at the end.
- The command is fully covered by automated tests in `tests/test_one_shot_command.py`.

## Error Handling
- If any step fails, execution stops immediately and an error is printed.
- No further steps are run after a failure.

## Testing
- Tests cover minimal and option-rich invocations, error cases, and output validation.

## References
- See requirements, user stories, and CLI documentation for details.
