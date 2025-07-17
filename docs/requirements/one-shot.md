# Requirements: One-Shot Command

## Overview
The one-shot command provides a single CLI entry point to run the entire file copy workflow (init, import, add-source, analyze, checksum, copy, verify, summary) in one step, with robust error handling and user-friendly options.

## Requirements
- The command must be named `one-shot` and available as a subcommand in the CLI.
- It must accept all required arguments for the full workflow: `--job-dir`, `--job-name`, `--src`, `--dst`.
- It must support all relevant options: `--threads`, `--no-progress`, `--log-level`, `--resume`, `--reverify`, `--checksum-db`, `--other-db`, `--table`, `--stage`, `--skip-verify`.
- The workflow must execute the following steps in order:
  1. Initialize job directory
  2. Import checksums (if provided)
  3. Add source files
  4. Add to destination index pool
  5. Analyze
  6. Compute checksums (source, then destination)
  7. Copy files
  8. Verify (shallow, then deep if requested)
  9. Print summary
- If any step fails, the workflow must stop immediately and print an error message.
- On success, print "Done" at the end.
- All steps must use the same argument values as if run individually.
- The command must be fully tested with minimal and option-rich invocations.

## Non-Requirements
- No GUI or interactive prompts.
- No support for legacy job database formats.

## References
- See user stories and CLI documentation for usage scenarios and options.
