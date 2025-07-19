# Requirements: One-Shot Phase

## Overview
The one-shot phase runs the full deduplication workflow (init, analyze, move, verify, summary) in a single CLI invocation.

## Requirements
- The CLI must provide a `one-shot` subcommand.
- Must accept all required arguments for the full workflow: `--job-dir`, `--job-name`, `--lookup-pool`, `--dupes-folder`.
- Must execute all workflow phases in order: init, analyze, move, verify, summary.
- Must stop immediately and print an error if any phase fails.
- Must print "Done" on success.
- Must be fully tested with minimal and option-rich invocations.

## References
- See implementation/one-shot.md and feature/one-shot.md for details.
