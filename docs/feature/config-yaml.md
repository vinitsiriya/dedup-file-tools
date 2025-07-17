# Feature: YAML Configuration Option (`-c`)

## Summary
The tool supports a `-c <config.yaml>` or `--config <config.yaml>` option to load all CLI options from a YAML configuration file, simplifying usage for complex or repeatable workflows.

## Usage
- Add `-c config.yaml` to any command to load options from the YAML file.
- CLI arguments always override YAML config values if both are provided.
- The YAML file supports all CLI options as documented in the CLI reference.

## Example YAML
```yaml
command: one-shot
job_dir: /path/to/job
dst:
  - /mnt/dest1
src:
  - /mnt/source1
threads: 8
log_level: DEBUG
```

## Notes
- The feature is fully backward compatible: if `-c` is not used, the tool works as before.
- See CLI documentation for a full list of supported options and YAML keys.
- See requirements and implementation docs for technical details.
