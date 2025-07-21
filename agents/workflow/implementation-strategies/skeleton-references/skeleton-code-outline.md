# dedup-file-tools: Skeleton Code Reference

This document provides an outline of the code structure for the dedup-file-tools project, based on the current skeleton files. It is intended as a reference for developers and agents to quickly understand the organization and main entry points of the codebase.

---

## Top-Level Modules

- **dedup_file_tools_commons/**
  - `__init__.py`: Commons package init
  - `db.py`: Common database helpers and schema logic
  - `utils/`: Shared utilities
    - `checksum_cache.py`, `checksum_cache2.py`: Checksum cache logic
    - `db_utils.py`: Database utility functions
    - `fileops.py`: File operations and helpers
    - `logging_config.py`: Logging setup
    - `paths.py`: Path utilities
    - `robust_sqlite.py`: Robust SQLite helpers
    - `uidpath.py`: System-independent path abstraction

- **dedup_file_tools_dupes_move/**
  - `__init__.py`: Module init
  - `cli.py`: CLI entry point
  - `db.py`: Deduplication DB schema/logic
  - `handlers.py`: CLI/phase handler functions
  - `main.py`: Main CLI logic and argument parsing
  - `phases/`: Phase-based logic
    - `analysis.py`: Duplicate analysis
    - `move.py`: Move phase
    - `preview_summary.py`, `summary.py`, `verify.py`: Reporting and verification
  - `utils/`: Config loader and helpers

- **dedup_file_tools_fs_copy/**
  - `__init__.py`: Module init
  - `db.py`: Copy tool DB schema/logic
  - `main.py`: Main CLI logic and argument parsing
  - `phases/`: Phase-based logic
    - `analysis.py`: Directory analysis
    - `checksum.py`: Checksum computation
    - `copy.py`: File copy logic
    - `ensure_destination_pool.py`, `import_checksum.py`: Pool and import helpers
    - `summary.py`, `verify.py`: Reporting and verification
  - `utils/`: Config loader, destination pool, and helpers

- **e2e_tests/**, **tests/**: End-to-end and unit tests for all modules
- **scripts/**: Utility scripts for fixture generation and migration
- **manual_tests/**: Manual test helpers

---

## Main Entry Points

- `dedup_file_tools_dupes_move.main:main(argv)`
- `dedup_file_tools_fs_copy.main:main(args)`
- CLI wrappers in `cli.py` for each module

---

## Key Patterns

- **Phase-based workflow:** Each major operation (analyze, copy, move, verify) is implemented as a phase in its own module.
- **Handler dispatch:** CLI commands are mapped to handler functions in `handlers.py` or `main.py`.
- **Config loading:** YAML config support with CLI override pattern.
- **Database abstraction:** All persistent state is managed via SQLite, with robust connection helpers.
- **UidPath abstraction:** All file references use (uid, relative_path) for portability.

---


Directory Structure:

./
.skpy-skeleton/
    SKELETON_MAPPING.md
    dedup_file_tools_commons/
        __init__.skpy
        db.skpy
        utils/
            __init__.skpy
            checksum_cache.skpy
            checksum_cache2.skpy
            db_utils.skpy
            fileops.skpy
            logging_config.skpy
            paths.skpy
            robust_sqlite.skpy
            uidpath.skpy
    dedup_file_tools_dupes_move/
        __init__.skpy
        cli.skpy
        db.skpy
        handlers.skpy
        main.skpy
        phases/
            __init__.skpy
            analysis.skpy
            move.skpy
            preview_summary.skpy
            summary.skpy
            verify.skpy
        tests/
            __init__.skpy
        utils/
            __init__.skpy
            config_loader.skpy
    dedup_file_tools_fs_copy/
        __init__.skpy
        db.skpy
        main.skpy
        phases/
            __init__.skpy
            analysis.skpy
            checksum.skpy
            copy.skpy
            ensure_destination_pool.skpy
            import_checksum.skpy
            summary.skpy
            verify.skpy
        utils/
            __init__.skpy
            config_loader.skpy
            destination_pool.skpy
            destination_pool_cli.skpy
            interactive_config.skpy
    e2e_tests/
        test_e2e_import_checksums.skpy
        test_incremental_checksums.skpy
        test_integration_cases.skpy
        test_partial_dst_prepop.skpy
    manual_tests/
        dedup_file_tools_dupes_move/
            generate_fixtures_manual.skpy
    scripts/
        generate_fixtures.skpy
        generate_fixtures_manual.skpy
        migrate_status_fields.skpy
    setup.skpy
    tests/
        __init__.skpy
        dedup_file_tools_dupes_commons/
            __init__.skpy
            test_checksum_cache.skpy
            test_checksum_cache_invalidation.skpy
            test_checksum_cache_more.skpy
            test_fileops.skpy
            test_uidpath.skpy
            test_uidpath_discovery.skpy
            test_uidpath_real_scenarios.skpy
        dedup_file_tools_dupes_move/
            __init__.skpy
            test_analysis.skpy
            test_cli_workflow_move.skpy
            test_config_loader.skpy
            test_extra_workflow.skpy
            test_import_checksums.skpy
            test_one_shot_command.skpy
            test_provenance_path_preservation.skpy
        dedup_file_tools_fs_copy/
            __init__.skpy
            test_analysis.skpy
            test_cli_config_integration.skpy
            test_cli_config_yaml.skpy
            test_cli_init_config.skpy
            test_cli_workflow_copy.skpy
            test_cli_workflow_verify_deep.skpy
            test_cli_workflow_verify_shallow.skpy
            test_config_loader.skpy
            test_copy_with_destination_pool.skpy
            test_destination_pool_cache_validation.skpy
            test_destination_pool_cli.skpy
            test_destination_pool_index.skpy
            test_generate_config.skpy
            test_handle_resume.skpy
            test_import_checksums.skpy
            test_one_shot_command.skpy
            test_summary.skpy
File Contents:
==========.skpy-skeleton\setup.skpy:
from setuptools import setup, find_packages


==========.skpy-skeleton\SKELETON_MAPPING.md:
# Skeleton Directory Skip/Mapping Guide

This directory contains skeleton files generated from the original Python source files.

## How to Use
- Each `.skpy` file here is a skeleton version of a real Python file from your codebase.
- The original location of each file is recorded below.
- Use this mapping to find the source file for any skeleton.

**Source root:** `.`

**Skeleton output root:** `.skpy-skeleton`

> The table below maps each generated skeleton file (left column) to its original Python source file (right column). All paths are relative to their respective root directories listed above. Use this mapping to trace any skeleton back to its source.

## Skeleton File Mapping

| Skeleton File | Original Source File |
|--------------|---------------------|
| build\lib\dedup_file_tools_commons\__init__.skpy | build\lib\dedup_file_tools_commons\__init__.py |
| build\lib\dedup_file_tools_commons\db.skpy | build\lib\dedup_file_tools_commons\db.py |
| build\lib\dedup_file_tools_commons\utils\__init__.skpy | build\lib\dedup_file_tools_commons\utils\__init__.py |
| build\lib\dedup_file_tools_commons\utils\checksum_cache.skpy | build\lib\dedup_file_tools_commons\utils\checksum_cache.py |
| build\lib\dedup_file_tools_commons\utils\db_utils.skpy | build\lib\dedup_file_tools_commons\utils\db_utils.py |
| build\lib\dedup_file_tools_commons\utils\fileops.skpy | build\lib\dedup_file_tools_commons\utils\fileops.py |
| build\lib\dedup_file_tools_commons\utils\logging_config.skpy | build\lib\dedup_file_tools_commons\utils\logging_config.py |
| build\lib\dedup_file_tools_commons\utils\paths.skpy | build\lib\dedup_file_tools_commons\utils\paths.py |
| build\lib\dedup_file_tools_commons\utils\robust_sqlite.skpy | build\lib\dedup_file_tools_commons\utils\robust_sqlite.py |
| build\lib\dedup_file_tools_commons\utils\uidpath.skpy | build\lib\dedup_file_tools_commons\utils\uidpath.py |
| build\lib\dedup_file_tools_dupes_move\__init__.skpy | build\lib\dedup_file_tools_dupes_move\__init__.py |
| build\lib\dedup_file_tools_dupes_move\cli.skpy | build\lib\dedup_file_tools_dupes_move\cli.py |
| build\lib\dedup_file_tools_dupes_move\db.skpy | build\lib\dedup_file_tools_dupes_move\db.py |
| build\lib\dedup_file_tools_dupes_move\handlers.skpy | build\lib\dedup_file_tools_dupes_move\handlers.py |
| build\lib\dedup_file_tools_dupes_move\main.skpy | build\lib\dedup_file_tools_dupes_move\main.py |
| build\lib\dedup_file_tools_dupes_move\phases\__init__.skpy | build\lib\dedup_file_tools_dupes_move\phases\__init__.py |
| build\lib\dedup_file_tools_dupes_move\phases\analysis.skpy | build\lib\dedup_file_tools_dupes_move\phases\analysis.py |
| build\lib\dedup_file_tools_dupes_move\phases\move.skpy | build\lib\dedup_file_tools_dupes_move\phases\move.py |
| build\lib\dedup_file_tools_dupes_move\phases\preview_summary.skpy | build\lib\dedup_file_tools_dupes_move\phases\preview_summary.py |
| build\lib\dedup_file_tools_dupes_move\phases\summary.skpy | build\lib\dedup_file_tools_dupes_move\phases\summary.py |
| build\lib\dedup_file_tools_dupes_move\phases\verify.skpy | build\lib\dedup_file_tools_dupes_move\phases\verify.py |
| build\lib\dedup_file_tools_dupes_move\tests\__init__.skpy | build\lib\dedup_file_tools_dupes_move\tests\__init__.py |
| build\lib\dedup_file_tools_dupes_move\utils\__init__.skpy | build\lib\dedup_file_tools_dupes_move\utils\__init__.py |
| build\lib\dedup_file_tools_dupes_move\utils\config_loader.skpy | build\lib\dedup_file_tools_dupes_move\utils\config_loader.py |
| build\lib\dedup_file_tools_fs_copy\__init__.skpy | build\lib\dedup_file_tools_fs_copy\__init__.py |
| build\lib\dedup_file_tools_fs_copy\db.skpy | build\lib\dedup_file_tools_fs_copy\db.py |
| build\lib\dedup_file_tools_fs_copy\main.skpy | build\lib\dedup_file_tools_fs_copy\main.py |
| build\lib\dedup_file_tools_fs_copy\phases\__init__.skpy | build\lib\dedup_file_tools_fs_copy\phases\__init__.py |
| build\lib\dedup_file_tools_fs_copy\phases\analysis.skpy | build\lib\dedup_file_tools_fs_copy\phases\analysis.py |
| build\lib\dedup_file_tools_fs_copy\phases\copy.skpy | build\lib\dedup_file_tools_fs_copy\phases\copy.py |
| build\lib\dedup_file_tools_fs_copy\phases\summary.skpy | build\lib\dedup_file_tools_fs_copy\phases\summary.py |
| build\lib\dedup_file_tools_fs_copy\phases\verify.skpy | build\lib\dedup_file_tools_fs_copy\phases\verify.py |
| build\lib\dedup_file_tools_fs_copy\utils\__init__.skpy | build\lib\dedup_file_tools_fs_copy\utils\__init__.py |
| build\lib\dedup_file_tools_fs_copy\utils\config_loader.skpy | build\lib\dedup_file_tools_fs_copy\utils\config_loader.py |
| build\lib\dedup_file_tools_fs_copy\utils\destination_pool.skpy | build\lib\dedup_file_tools_fs_copy\utils\destination_pool.py |
| build\lib\dedup_file_tools_fs_copy\utils\destination_pool_cli.skpy | build\lib\dedup_file_tools_fs_copy\utils\destination_pool_cli.py |
| build\lib\dedup_file_tools_fs_copy\utils\interactive_config.skpy | build\lib\dedup_file_tools_fs_copy\utils\interactive_config.py |
| build\lib\tests\__init__.skpy | build\lib\tests\__init__.py |
| build\lib\tests\dedup_file_tools_dupes_commons\__init__.skpy | build\lib\tests\dedup_file_tools_dupes_commons\__init__.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_checksum_cache.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_checksum_cache.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_checksum_cache_invalidation.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_checksum_cache_invalidation.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_checksum_cache_more.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_checksum_cache_more.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_fileops.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_fileops.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_uidpath.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_uidpath.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_uidpath_discovery.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_uidpath_discovery.py |
| build\lib\tests\dedup_file_tools_dupes_commons\test_uidpath_real_scenarios.skpy | build\lib\tests\dedup_file_tools_dupes_commons\test_uidpath_real_scenarios.py |
| build\lib\tests\dedup_file_tools_dupes_move\__init__.skpy | build\lib\tests\dedup_file_tools_dupes_move\__init__.py |
| build\lib\tests\dedup_file_tools_dupes_move\test_analysis.skpy | build\lib\tests\dedup_file_tools_dupes_move\test_analysis.py |
| build\lib\tests\dedup_file_tools_dupes_move\test_cli_workflow_move.skpy | build\lib\tests\dedup_file_tools_dupes_move\test_cli_workflow_move.py |
| build\lib\tests\dedup_file_tools_dupes_move\test_config_loader.skpy | build\lib\tests\dedup_file_tools_dupes_move\test_config_loader.py |
| build\lib\tests\dedup_file_tools_dupes_move\test_extra_workflow.skpy | build\lib\tests\dedup_file_tools_dupes_move\test_extra_workflow.py |
| build\lib\tests\dedup_file_tools_dupes_move\test_one_shot_command.skpy | build\lib\tests\dedup_file_tools_dupes_move\test_one_shot_command.py |
| build\lib\tests\dedup_file_tools_fs_copy\__init__.skpy | build\lib\tests\dedup_file_tools_fs_copy\__init__.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_analysis.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_analysis.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_cli_config_integration.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_cli_config_integration.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_cli_config_yaml.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_cli_config_yaml.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_cli_init_config.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_cli_init_config.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_cli_workflow_copy.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_cli_workflow_copy.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_deep.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_deep.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_shallow.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_shallow.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_config_loader.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_config_loader.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_copy_with_destination_pool.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_copy_with_destination_pool.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_destination_pool_cache_validation.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_destination_pool_cache_validation.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_destination_pool_cli.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_destination_pool_cli.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_destination_pool_index.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_destination_pool_index.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_generate_config.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_generate_config.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_handle_resume.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_handle_resume.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_import_checksums.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_import_checksums.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_one_shot_command.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_one_shot_command.py |
| build\lib\tests\dedup_file_tools_fs_copy\test_summary.skpy | build\lib\tests\dedup_file_tools_fs_copy\test_summary.py |
| dedup_file_tools_commons\__init__.skpy | dedup_file_tools_commons\__init__.py |
| dedup_file_tools_commons\db.skpy | dedup_file_tools_commons\db.py |
| dedup_file_tools_commons\utils\__init__.skpy | dedup_file_tools_commons\utils\__init__.py |
| dedup_file_tools_commons\utils\checksum_cache.skpy | dedup_file_tools_commons\utils\checksum_cache.py |
| dedup_file_tools_commons\utils\checksum_cache2.skpy | dedup_file_tools_commons\utils\checksum_cache2.py |
| dedup_file_tools_commons\utils\db_utils.skpy | dedup_file_tools_commons\utils\db_utils.py |
| dedup_file_tools_commons\utils\fileops.skpy | dedup_file_tools_commons\utils\fileops.py |
| dedup_file_tools_commons\utils\logging_config.skpy | dedup_file_tools_commons\utils\logging_config.py |
| dedup_file_tools_commons\utils\paths.skpy | dedup_file_tools_commons\utils\paths.py |
| dedup_file_tools_commons\utils\robust_sqlite.skpy | dedup_file_tools_commons\utils\robust_sqlite.py |
| dedup_file_tools_commons\utils\uidpath.skpy | dedup_file_tools_commons\utils\uidpath.py |
| dedup_file_tools_dupes_move\__init__.skpy | dedup_file_tools_dupes_move\__init__.py |
| dedup_file_tools_dupes_move\cli.skpy | dedup_file_tools_dupes_move\cli.py |
| dedup_file_tools_dupes_move\db.skpy | dedup_file_tools_dupes_move\db.py |
| dedup_file_tools_dupes_move\handlers.skpy | dedup_file_tools_dupes_move\handlers.py |
| dedup_file_tools_dupes_move\main.skpy | dedup_file_tools_dupes_move\main.py |
| dedup_file_tools_dupes_move\phases\__init__.skpy | dedup_file_tools_dupes_move\phases\__init__.py |
| dedup_file_tools_dupes_move\phases\analysis.skpy | dedup_file_tools_dupes_move\phases\analysis.py |
| dedup_file_tools_dupes_move\phases\move.skpy | dedup_file_tools_dupes_move\phases\move.py |
| dedup_file_tools_dupes_move\phases\preview_summary.skpy | dedup_file_tools_dupes_move\phases\preview_summary.py |
| dedup_file_tools_dupes_move\phases\summary.skpy | dedup_file_tools_dupes_move\phases\summary.py |
| dedup_file_tools_dupes_move\phases\verify.skpy | dedup_file_tools_dupes_move\phases\verify.py |
| dedup_file_tools_dupes_move\tests\__init__.skpy | dedup_file_tools_dupes_move\tests\__init__.py |
| dedup_file_tools_dupes_move\utils\__init__.skpy | dedup_file_tools_dupes_move\utils\__init__.py |
| dedup_file_tools_dupes_move\utils\config_loader.skpy | dedup_file_tools_dupes_move\utils\config_loader.py |
| dedup_file_tools_fs_copy\__init__.skpy | dedup_file_tools_fs_copy\__init__.py |
| dedup_file_tools_fs_copy\db.skpy | dedup_file_tools_fs_copy\db.py |
| dedup_file_tools_fs_copy\main.skpy | dedup_file_tools_fs_copy\main.py |
| dedup_file_tools_fs_copy\phases\__init__.skpy | dedup_file_tools_fs_copy\phases\__init__.py |
| dedup_file_tools_fs_copy\phases\analysis.skpy | dedup_file_tools_fs_copy\phases\analysis.py |
| dedup_file_tools_fs_copy\phases\checksum.skpy | dedup_file_tools_fs_copy\phases\checksum.py |
| dedup_file_tools_fs_copy\phases\copy.skpy | dedup_file_tools_fs_copy\phases\copy.py |
| dedup_file_tools_fs_copy\phases\ensure_destination_pool.skpy | dedup_file_tools_fs_copy\phases\ensure_destination_pool.py |
| dedup_file_tools_fs_copy\phases\import_checksum.skpy | dedup_file_tools_fs_copy\phases\import_checksum.py |
| dedup_file_tools_fs_copy\phases\summary.skpy | dedup_file_tools_fs_copy\phases\summary.py |
| dedup_file_tools_fs_copy\phases\verify.skpy | dedup_file_tools_fs_copy\phases\verify.py |
| dedup_file_tools_fs_copy\utils\__init__.skpy | dedup_file_tools_fs_copy\utils\__init__.py |
| dedup_file_tools_fs_copy\utils\config_loader.skpy | dedup_file_tools_fs_copy\utils\config_loader.py |
| dedup_file_tools_fs_copy\utils\destination_pool.skpy | dedup_file_tools_fs_copy\utils\destination_pool.py |
| dedup_file_tools_fs_copy\utils\destination_pool_cli.skpy | dedup_file_tools_fs_copy\utils\destination_pool_cli.py |
| dedup_file_tools_fs_copy\utils\interactive_config.skpy | dedup_file_tools_fs_copy\utils\interactive_config.py |
| e2e_tests\test_e2e_import_checksums.skpy | e2e_tests\test_e2e_import_checksums.py |
| e2e_tests\test_incremental_checksums.skpy | e2e_tests\test_incremental_checksums.py |
| e2e_tests\test_integration_cases.skpy | e2e_tests\test_integration_cases.py |
| e2e_tests\test_partial_dst_prepop.skpy | e2e_tests\test_partial_dst_prepop.py |
| manual_tests\dedup_file_tools_dupes_move\generate_fixtures_manual.skpy | manual_tests\dedup_file_tools_dupes_move\generate_fixtures_manual.py |
| scripts\generate_fixtures.skpy | scripts\generate_fixtures.py |
| scripts\generate_fixtures_manual.skpy | scripts\generate_fixtures_manual.py |
| scripts\migrate_status_fields.skpy | scripts\migrate_status_fields.py |
| setup.skpy | setup.py |
| tests\__init__.skpy | tests\__init__.py |
| tests\dedup_file_tools_dupes_commons\__init__.skpy | tests\dedup_file_tools_dupes_commons\__init__.py |
| tests\dedup_file_tools_dupes_commons\test_checksum_cache.skpy | tests\dedup_file_tools_dupes_commons\test_checksum_cache.py |
| tests\dedup_file_tools_dupes_commons\test_checksum_cache_invalidation.skpy | tests\dedup_file_tools_dupes_commons\test_checksum_cache_invalidation.py |
| tests\dedup_file_tools_dupes_commons\test_checksum_cache_more.skpy | tests\dedup_file_tools_dupes_commons\test_checksum_cache_more.py |
| tests\dedup_file_tools_dupes_commons\test_fileops.skpy | tests\dedup_file_tools_dupes_commons\test_fileops.py |
| tests\dedup_file_tools_dupes_commons\test_uidpath.skpy | tests\dedup_file_tools_dupes_commons\test_uidpath.py |
| tests\dedup_file_tools_dupes_commons\test_uidpath_discovery.skpy | tests\dedup_file_tools_dupes_commons\test_uidpath_discovery.py |
| tests\dedup_file_tools_dupes_commons\test_uidpath_real_scenarios.skpy | tests\dedup_file_tools_dupes_commons\test_uidpath_real_scenarios.py |
| tests\dedup_file_tools_dupes_move\__init__.skpy | tests\dedup_file_tools_dupes_move\__init__.py |
| tests\dedup_file_tools_dupes_move\test_analysis.skpy | tests\dedup_file_tools_dupes_move\test_analysis.py |
| tests\dedup_file_tools_dupes_move\test_cli_workflow_move.skpy | tests\dedup_file_tools_dupes_move\test_cli_workflow_move.py |
| tests\dedup_file_tools_dupes_move\test_config_loader.skpy | tests\dedup_file_tools_dupes_move\test_config_loader.py |
| tests\dedup_file_tools_dupes_move\test_extra_workflow.skpy | tests\dedup_file_tools_dupes_move\test_extra_workflow.py |
| tests\dedup_file_tools_dupes_move\test_import_checksums.skpy | tests\dedup_file_tools_dupes_move\test_import_checksums.py |
| tests\dedup_file_tools_dupes_move\test_one_shot_command.skpy | tests\dedup_file_tools_dupes_move\test_one_shot_command.py |
| tests\dedup_file_tools_dupes_move\test_provenance_path_preservation.skpy | tests\dedup_file_tools_dupes_move\test_provenance_path_preservation.py |
| tests\dedup_file_tools_fs_copy\__init__.skpy | tests\dedup_file_tools_fs_copy\__init__.py |
| tests\dedup_file_tools_fs_copy\test_analysis.skpy | tests\dedup_file_tools_fs_copy\test_analysis.py |
| tests\dedup_file_tools_fs_copy\test_cli_config_integration.skpy | tests\dedup_file_tools_fs_copy\test_cli_config_integration.py |
| tests\dedup_file_tools_fs_copy\test_cli_config_yaml.skpy | tests\dedup_file_tools_fs_copy\test_cli_config_yaml.py |
| tests\dedup_file_tools_fs_copy\test_cli_init_config.skpy | tests\dedup_file_tools_fs_copy\test_cli_init_config.py |
| tests\dedup_file_tools_fs_copy\test_cli_workflow_copy.skpy | tests\dedup_file_tools_fs_copy\test_cli_workflow_copy.py |
| tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_deep.skpy | tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_deep.py |
| tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_shallow.skpy | tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_shallow.py |
| tests\dedup_file_tools_fs_copy\test_config_loader.skpy | tests\dedup_file_tools_fs_copy\test_config_loader.py |
| tests\dedup_file_tools_fs_copy\test_copy_with_destination_pool.skpy | tests\dedup_file_tools_fs_copy\test_copy_with_destination_pool.py |
| tests\dedup_file_tools_fs_copy\test_destination_pool_cache_validation.skpy | tests\dedup_file_tools_fs_copy\test_destination_pool_cache_validation.py |
| tests\dedup_file_tools_fs_copy\test_destination_pool_cli.skpy | tests\dedup_file_tools_fs_copy\test_destination_pool_cli.py |
| tests\dedup_file_tools_fs_copy\test_destination_pool_index.skpy | tests\dedup_file_tools_fs_copy\test_destination_pool_index.py |
| tests\dedup_file_tools_fs_copy\test_generate_config.skpy | tests\dedup_file_tools_fs_copy\test_generate_config.py |
| tests\dedup_file_tools_fs_copy\test_handle_resume.skpy | tests\dedup_file_tools_fs_copy\test_handle_resume.py |
| tests\dedup_file_tools_fs_copy\test_import_checksums.skpy | tests\dedup_file_tools_fs_copy\test_import_checksums.py |
| tests\dedup_file_tools_fs_copy\test_one_shot_command.skpy | tests\dedup_file_tools_fs_copy\test_one_shot_command.py |
| tests\dedup_file_tools_fs_copy\test_summary.skpy | tests\dedup_file_tools_fs_copy\test_summary.py |

<!--
Replace <skeleton_file> and <original_file> with the actual relative paths.
This file is auto-generated by the skeleton extraction tool.
-->


==========.skpy-skeleton\dedup_file_tools_commons\db.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def init_checksum_db(checksum_db_path):
    pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\checksum_cache.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from typing import Optional
from pathlib import Path
from dedup_file_tools_commons.utils.fileops import compute_sha256
import time


class ChecksumCache:
    """Centralized access for all checksum cache operations.
    Uses UidPath for all conversions and file resolution."""

    def __init__(self, conn_factory, uid_path):
        pass

    def exists_at_paths(self, paths, checksum):
        pass

    def exists_at_uid_relpath_array(self, uid_relpath_list, checksum):
        pass

    def exists_at_destination(self, uid, rel_path):
        pass

    def exists_at_destination_checksum(self, checksum):
        pass

    def ensure_indexes(self):
        pass

    def get_or_compute_with_invalidation(self, path):
        pass

    def exists_at_destination_pool(self, checksum):
        pass

    def get(self, path):
        pass

    def exists(self, checksum):
        pass

    def insert_or_update(self, path, size, last_modified, checksum):
        pass

    def get_or_compute(self, path):
        pass

    def exists_at_destination_pool_legacy(self, checksum):
        pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\checksum_cache2.skpy:
from dedup_file_tools_commons.utils.fileops import compute_sha256
from pathlib import Path
from typing import Optional
import time


class ChecksumCache2:
    """Variant of ChecksumCache that takes a live DB connection object for all operations.
    This avoids opening/closing a connection for each query, and is suitable for batch operations.
    """

    def __init__(self, uid_path):
        pass

    def exists_at_paths(self, conn, paths, checksum):
        pass

    def exists_at_uid_relpath_array(self, conn, uid_relpath_list, checksum):
        pass

    def exists_at_destination(self, conn, uid, rel_path):
        pass

    def exists_at_destination_checksum(self, conn, checksum):
        pass

    def ensure_indexes(self, conn):
        pass

    def get_or_compute_with_invalidation(self, conn, path):
        pass

    def exists_at_destination_pool(self, conn, checksum):
        pass

    def get(self, conn, path):
        pass

    def exists(self, conn, checksum):
        pass

    def insert_or_update(self, conn, path, size, last_modified, checksum):
        pass

    def get_or_compute(self, conn, path):
        pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\db_utils.skpy:
import os
import logging
from dedup_file_tools_commons.db import init_checksum_db
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def connect_with_attached_checksum_db(main_db_path, checksum_db_path):
    """Ensure the checksum DB exists and has the correct schema, then attach it to the main DB connection as 'checksumdb'.
    Returns a sqlite3.Connection object with the checksum DB attached."""
    pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\fileops.skpy:
import shutil
import hashlib
from pathlib import Path
from tqdm import tqdm
import os


def copy_file(src, dst, block_size, progress_callback, show_progressbar):
    """Copy file from src to dst in blocks, with optional progress callback and per-file progressbar. Preserves mtime. File-level resume: always restarts file if interrupted."""
    pass


def verify_file(src, dst):
    """Verify that two files have the same SHA-256 checksum."""
    pass


def compute_sha256(file_path, block_size):
    pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\logging_config.skpy:
import logging
import os
import datetime


def setup_logging(job_dir, log_level):
    """Set up logging to a timestamped log file in the job_dir/logs directory.
    If job_dir is None, use 'changes/dedup_file_tools_fs_copy.log'.
    log_level can be passed as a string (e.g., 'INFO', 'DEBUG').
    If not provided, will use LOG_LEVEL environment variable, or default to 'INFO'."""
    pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\paths.skpy:
import os


def get_db_path_from_job_dir(job_dir, job_name):
    """Return the path to the main job database given the job directory and job name."""
    pass


def get_checksum_db_path(job_dir, checksum_db):
    """Return the path to the checksum database, using a custom path if provided."""
    pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\robust_sqlite.skpy:
import sqlite3
import time
from typing import Optional, Callable


class RobustSqliteConn:

    def __init__(self, db_path, timeout, retries, retry_delay, wal):
        pass

    def connect(self):
        pass

    def with_connection(self, fn):
        pass


==========.skpy-skeleton\dedup_file_tools_commons\utils\uidpath.skpy:
import platform
import logging
from pathlib import Path
import subprocess
from dataclasses import dataclass
from typing import Any


class UidPath:
    """UidPath: System-independent file reference.

    Represents a file location as a (uid, relative_path) pair:
    - uid: Unique identifier for the volume (serial number, UUID, or test path).
    - relative_path: Path relative to the mount point or root.

    Use this struct to pass file references around, instead of raw tuples."""

    uid: Any
    relative_path: str


class UidPathUtil:
    """UidPath provides methods to convert file paths to a (UID, relative_path) tuple and reconstruct
    absolute paths from these tuples. This abstraction allows for system-independent file referencing.

    UID:
        - On Windows: The volume serial number (replacement for drive letter, e.g., 'C:').
        - On Linux: The filesystem UUID.
    Relative Path:
        - The path of the file relative to the mount point (drive root or mount directory).
        - NOTE: The format of relative_path is only guaranteed to be relative to the detected mount point.
          It may be a long path segment or appear absolute in some environments (e.g., tests/temp dirs).
        - Only UidPath should interpret or manipulate rel_path; all other code should treat it as opaque.
    """

    def __init__(self):
        """Initialize UidPath, detecting the operating system and available mount points."""
        pass

    def get_mounts(self):
        """Detect all available mount points and their UIDs for the current system.
        Returns:
            dict: Mapping of mount point (str) to UID (str or int)."""
        pass

    def get_mounts_linux(self):
        """Get Linux mount points and their UUIDs using lsblk.
        Returns:
            dict: Mapping of mount point to UUID."""
        pass

    def get_mounts_windows(self):
        """Get Windows drive letters and their volume serial numbers using WMI.
        Returns:
            dict: Mapping of drive letter (e.g., 'C:') to serial number (int or str)."""
        pass

    def update_mounts(self):
        """Refresh the mount point to UID mapping."""
        pass

    def get_available_volumes(self):
        """Return the current mapping of mount points to UIDs.
        Returns:
            dict: Mapping of mount point to UID."""
        pass

    def is_volume_available(self, uid):
        """Check if a volume with the given UID is available.
        Args:
            uid (str or int): UID to check.
        Returns:
            bool: True if available, False otherwise."""
        pass

    def get_volume_id_from_path(self, path):
        """Get the UID for the given path.
        Args:
            path (str): Absolute file path.
        Returns:
            str or int: UID for the volume containing the path."""
        pass

    def get_mount_point_from_volume_id(self, volume_id):
        """Given a UID, return the corresponding mount point (drive root or mount directory).
        Args:
            volume_id (str or int): UID of the volume.
        Returns:
            str: Mount point path, or None if not found."""
        pass

    def get_available_uids(self):
        """Return a set of all available UIDs.
        Returns:
            set: Set of UIDs."""
        pass

    def convert_path(self, path):
        """Convert an absolute file path to a UidPath (uid, relative_path) struct.
        Args:
            path (str): Absolute file path.
        Returns:
            UidPath: (uid, relative_path) where relative_path is relative to the mount point.
        Notes:
            - The format of relative_path is only guaranteed to be relative to the detected mount point.
            - It may be a long path segment or appear absolute in some environments (e.g., tests/temp dirs).
            - Only UidPath should interpret or manipulate rel_path; all other code should treat it as opaque.
        """
        pass

    def reconstruct_path(self, uid_path_obj):
        """Reconstruct an absolute path from a UidPath (uid, relative_path) struct.
        Args:
            uid_path_obj (UidPath): UidPath dataclass with uid and relative_path.
        Returns:
            Path or None: Absolute path if the volume is available, else None."""
        pass

    def is_conversion_reversible(self, path):
        """Check if converting and reconstructing a path yields the original absolute path.
        Args:
            path (str): Absolute file path.
        Returns:
            bool: True if reversible, False otherwise."""
        pass

    def get_volume_label_from_drive_letter(self, drive_letter):
        """Get the volume label for a given drive letter (Windows only).
        Args:
            drive_letter (str): Drive letter (e.g., 'C:').
        Returns:
            str: Volume label, or 'Unknown' if not found."""
        pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\cli.skpy:
from dedup_file_tools_dupes_move.main import main


==========.skpy-skeleton\dedup_file_tools_dupes_move\db.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def init_db(db_path):
    pass


def init_dedupe_db(db_path):
    """Initialize all deduplication tables in the given database."""
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\handlers.skpy:
import logging
from dedup_file_tools_commons.utils.paths import (
    get_db_path_from_job_dir,
    get_checksum_db_path,
)
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
from dedup_file_tools_dupes_move.db import init_db


def handle_init(job_dir, job_name):
    pass


def handle_add_to_lookup_pool(job_dir, job_name, lookup_pool_root):
    pass


def handle_analyze(job_dir, job_name, dupes_folder, threads):
    pass


def handle_preview_summary(job_dir, job_name):
    pass


def handle_move(job_dir, job_name, dupes_folder, removal_folder, threads):
    pass


def handle_verify(job_dir, job_name, dupes_folder, removal_folder, threads):
    pass


def handle_summary(job_dir, job_name):
    pass


def handle_one_shot(job_dir, job_name, dupes_folder, removal_folder, threads):
    pass


def handle_import_checksums(job_dir, job_name, other_db, checksum_db, batch_size):
    """Import checksums from another compatible database's checksum_cache table into this job's checksum cache, using batched inserts for scalability."""
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\main.skpy:
import argparse
import logging
from dedup_file_tools_commons.utils.logging_config import setup_logging
from dedup_file_tools_dupes_move.utils.config_loader import (
    load_yaml_config,
    merge_config_with_args,
)
from dedup_file_tools_dupes_move.handlers import (
    handle_init,
    handle_add_to_lookup_pool,
    handle_analyze,
    handle_preview_summary,
    handle_move,
    handle_verify,
    handle_summary,
    handle_one_shot,
    handle_import_checksums,
)


def main(argv):
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\phases\analysis.skpy:
import os
from pathlib import Path
import logging
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def find_and_queue_duplicates(db_path, src_root, threads):
    """Scan src_root recursively, compute checksums, persist all file metadata to dedup_files_pool,
    group by checksum, and queue all but one file per group in dedup_move_plan."""
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\phases\move.skpy:
import os
import shutil
import time
from pathlib import Path
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def move_duplicates(db_path, dupes_folder, removal_folder, threads):
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\phases\preview_summary.skpy:
import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def preview_summary(db_path):
    """Print a summary of planned duplicate moves and groups before any file operations."""
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\phases\summary.skpy:
import csv
import os
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def summary_report(db_path, job_dir):
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\phases\verify.skpy:
import os
import time
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def verify_moves(db_path, dst_root, threads):
    pass


==========.skpy-skeleton\dedup_file_tools_dupes_move\utils\config_loader.skpy:
import yaml
import argparse
import os


def load_yaml_config(config_path):
    pass


def merge_config_with_args(args, config_dict, parser):
    """Update the argparse.Namespace `args` with values from config_dict,
    but only for arguments that are still set to their default values.
    CLI args always take precedence."""
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\db.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def init_db(db_path):
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\main.skpy:
from dedup_file_tools_commons.utils.logging_config import setup_logging
from dedup_file_tools_commons.db import init_checksum_db
import argparse
import logging
import sys
import os
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from pathlib import Path
from dedup_file_tools_fs_copy.db import init_db
from dedup_file_tools_fs_copy.phases.analysis import analyze_directories
from dedup_file_tools_fs_copy.phases.copy import copy_files
from dedup_file_tools_fs_copy.phases.verify import (
    shallow_verify_files,
    deep_verify_files,
)
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.paths import (
    get_db_path_from_job_dir,
    get_checksum_db_path,
)
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db


def handle_add_to_destination_index_pool(args):
    pass


def init_job_dir(job_dir, job_name, checksum_db):
    pass


def add_file_to_db(db_path, file_path):
    pass


def add_source_to_db(db_path, src_dir):
    pass


def list_files_in_db(db_path):
    pass


def remove_file_from_db(db_path, file_path):
    pass


def parse_args(args):
    pass


def main(args):
    pass


def handle_summary(args):
    pass


def handle_init(args):
    pass


def handle_analyze(args):
    pass


def handle_copy(args):
    pass


def handle_verify(args):
    pass


def handle_resume(args):
    pass


def handle_status(args):
    pass


def handle_log(args):
    pass


def handle_deep_verify(args):
    pass


def handle_verify_status(args):
    pass


def handle_deep_verify_status(args):
    pass


def handle_add_file(args):
    pass


def handle_add_source(args):
    pass


def handle_list_files(args):
    pass


def handle_remove_file(args):
    pass


def handle_checksum(args):
    pass


def handle_import_checksums(args):
    pass


def run_main_command(args):
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\analysis.skpy:
import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from pathlib import Path
import os
from tqdm import tqdm


def persist_file_metadata(db_path, table, file_info):
    pass


def scan_file_on_directory(directory_root, uid_path):
    pass


def analyze_directories(db_path, directory_roots, table):
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\checksum.skpy:
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sqlite3


def run_checksum_table(db_path, checksum_db_path, table, threads, no_progress):
    """Compute or update checksums for all files in the given table (source_files or destination_files)."""
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\copy.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.fileops import copy_file
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
import threading
import logging


def reset_status_for_missing_files(db_path, dst_roots):
    """For any file marked as done but missing from all destination roots, reset its status to 'pending'."""
    pass


def get_pending_copies(db_path):
    pass


def mark_copy_status(db_path, uid, rel_path, status, error_message):
    pass


def copy_files(db_path, src_roots, dst_roots, threads):
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\ensure_destination_pool.skpy:
from dedup_file_tools_commons.utils.paths import (
    get_db_path_from_job_dir,
    get_checksum_db_path,
)
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from tqdm import tqdm
import logging


def ensure_destination_pool_checksums(job_dir, job_name, checksum_db):
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\import_checksum.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
from tqdm import tqdm
import logging
import sys


def run_import_checksums(db_path, checksum_db_path, other_db_path):
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\summary.skpy:
import os
import csv
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn


def summary_phase(db_path, job_dir):
    """Prints a summary of what has happened, where the logs are, and generates a CSV report of errors and not-done files."""
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\phases\verify.skpy:
import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
import time
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPath, UidPathUtil


def verify_files(db_path, stage, reverify):
    """Unified verify function: runs shallow or deep verification based on stage.
    Args:
        db_path (str): Path to job database.
        stage (str): 'shallow' or 'deep'.
        reverify (bool): If True, clear previous verification results before running."""
    pass


def shallow_verify_files(db_path, reverify, max_workers):
    """Shallow verification: check file existence, size, and last modified time. Now multithreaded."""
    pass


def deep_verify_files(db_path, reverify, max_workers):
    """Deep verification: always perform all shallow checks, then compare checksums. Now multithreaded."""
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\utils\config_loader.skpy:
import yaml
import argparse
import os


def load_yaml_config(config_path):
    pass


def merge_config_with_args(args, config_dict, parser):
    """Update the argparse.Namespace `args` with values from config_dict,
    but only for arguments that are still set to their default values.
    CLI args always take precedence."""
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\utils\destination_pool.skpy:
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
import time


class DestinationPoolIndex:
    """Manages the destination pool index for global duplicate detection.
    This does NOT store checksums, only tracks which files are in the pool (by uid and relative path).
    Checksum management remains in checksum_cache.py."""

    def __init__(self, uid_path):
        pass

    def add_or_update_file(self, conn, path, size, last_modified):
        pass

    def exists(self, conn, uid, rel_path):
        pass

    def all_files(self, conn):
        pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\utils\destination_pool_cli.skpy:
import logging
from pathlib import Path
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from .destination_pool import DestinationPoolIndex


def add_to_destination_index_pool(db_path, dst_root):
    """Recursively scan dst_root and add/update all files in the destination pool index."""
    pass


==========.skpy-skeleton\dedup_file_tools_fs_copy\utils\interactive_config.skpy:
import yaml
import os


def interactive_config_generator():
    pass


==========.skpy-skeleton\e2e_tests\test_e2e_import_checksums.skpy:
import sqlite3
from dedup_file_tools_fs_copy import main
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
import pytest


def test_e2e_import_checksums(tmp_path):
    """E2E: Simulate two jobs, generate checksums in one, import into another, verify correctness."""
    pass


==========.skpy-skeleton\e2e_tests\test_incremental_checksums.skpy:
import os
import shutil
import subprocess
import sqlite3
from pathlib import Path


def test_incremental_checksums(tmp_path):
    """E2E: Handles cases where some checksums are already loaded.
    - Step 1: Create src with fileA, fileB. Run checksum (fileA, fileB).
    - Step 2: Add fileC, modify fileA, delete fileB. Run checksum again.
    - Step 3: Only fileA (changed) and fileC (new) should be rechecksummed/copied.
    - Step 4: fileB's checksum may remain in DB, but file should not be copied."""
    pass


==========.skpy-skeleton\e2e_tests\test_integration_cases.skpy:
import os
import shutil
import subprocess
from pathlib import Path


def test_deduplication(tmp_path):
    """E2E test: Deduplication scenario.
    - Source and destination have identical files.
    - After copy: no files should be copied/overwritten."""
    pass


def test_nested_directories(tmp_path):
    """E2E test: Nested directories scenario.
    - Source contains nested folders/files.
    - All files and structure should be copied to destination (current tool copies to dst/<full_source_path>).
    """
    pass


==========.skpy-skeleton\e2e_tests\test_partial_dst_prepop.skpy:
import os
import shutil
import subprocess
from pathlib import Path


def test_partial_dst_prepop(tmp_path):
    """E2E test: Partial destination prepopulation scenario.
    - Source: fileA, fileB, fileC, fileD
    - Destination prepopulated with fileA, fileC
    - After copy: fileB, fileD should be copied; fileA, fileC should remain unchanged
    - (Current tool copies to dst/<full_source_path>)"""
    pass


==========.skpy-skeleton\manual_tests\dedup_file_tools_dupes_move\generate_fixtures_manual.skpy:
import os


def generate_files(pool_dir):
    pass


==========.skpy-skeleton\scripts\generate_fixtures.skpy:
import os
import sys
import argparse
from pathlib import Path


def main():
    pass


==========.skpy-skeleton\scripts\generate_fixtures_manual.skpy:
import os
import argparse
from pathlib import Path
import shutil
import logging


def create_tree(root, depth, width, files_per_folder, prefix):
    pass


def create_tree_with_dups(root):
    """Create a clear deduplication test structure with descriptive names."""
    pass


def create_tree_with_dupes_in_dirs(root):
    """Create duplicate files with the same content in different directories for deduplication tests."""
    pass


def main():
    pass


==========.skpy-skeleton\scripts\migrate_status_fields.skpy:
import sqlite3
import sys


def migrate_status_fields(db_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_commons\test_checksum_cache.skpy:
import sqlite3
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def setup_test_db(tmp_path):
    pass


def test_insert_and_get(tmp_path):
    pass


def test_get_or_compute(tmp_path):
    pass


def test_exists(tmp_path):
    pass


def test_get_missing(tmp_path):
    pass


def test_get_or_compute_missing_file(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_commons\test_checksum_cache_invalidation.skpy:
import sqlite3
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def setup_test_db(tmp_path):
    pass


def test_get_or_compute_with_invalidation_basic(tmp_path):
    pass


def test_get_or_compute_with_invalidation_file_changed(tmp_path):
    pass


def test_get_or_compute_with_invalidation_file_metadata_changed(tmp_path):
    pass


def test_get_or_compute_with_invalidation_missing_file(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_commons\test_checksum_cache_more.skpy:
import sqlite3
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def setup_test_db_with_pool(tmp_path):
    pass


def test_exists_at_destination_pool(tmp_path):
    pass


def setup_test_db(tmp_path):
    pass


def test_update_existing_entry(tmp_path):
    pass


def test_multiple_files_and_uids(tmp_path):
    pass


def test_invalid_entries_are_ignored(tmp_path):
    pass


def test_subdirectory_file(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_commons\test_fileops.skpy:
from dedup_file_tools_commons.utils.fileops import copy_file, verify_file


def test_copy_file(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_commons\test_uidpath_discovery.skpy:
import os
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def test_pytest_discovery():
    pass


def test_convert_and_reconstruct(tmp_path):
    pass


def test_is_conversion_reversible(tmp_path):
    pass


def test_get_mounts_and_uids():
    pass


def test_nested_directory_conversion(tmp_path):
    pass


def test_get_mount_point_and_label():
    pass


def test_invalid_path_conversion():
    pass


def test_is_volume_available():
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_analysis.skpy:
import os
import sqlite3
import tempfile
from pathlib import Path
import pytest
from dedup_file_tools_dupes_move.phases.analysis import find_and_queue_duplicates
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def setup_test_db(tmp_path):
    pass


def test_find_and_queue_duplicates(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_cli_workflow_move.skpy:
import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_dupes_move.main import main


def test_cli_workflow_move(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_config_loader.skpy:
import tempfile
import os
import yaml
from dedup_file_tools_dupes_move.utils import config_loader


def test_load_yaml_config(tmp_path):
    pass


def test_merge_config_with_args():
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_extra_workflow.skpy:
import os
import shutil
import tempfile
import pytest
from dedup_file_tools_dupes_move.main import main


def test_analysis_detects_no_duplicates(tmp_path):
    pass


def test_move_handles_missing_file(tmp_path):
    pass


def test_verify_detects_checksum_mismatch(tmp_path):
    pass


def test_summary_csv_output(tmp_path):
    pass


def test_preview_summary_output(tmp_path, capsys):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_import_checksums.skpy:
import os
import sqlite3
import tempfile
import shutil
import pytest
from dedup_file_tools_dupes_move.handlers import handle_import_checksums
from dedup_file_tools_commons.utils.paths import (
    get_db_path_from_job_dir,
    get_checksum_db_path,
)


def create_test_db_with_checksums(db_path, checksums):
    pass


def test_handle_import_checksums(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_one_shot_command.skpy:
import pytest
import os
from dedup_file_tools_dupes_move.main import main


def test_one_shot_command(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_dupes_move\test_provenance_path_preservation.skpy:
import os
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_dupes_move.main import main


def test_pool_base_path_and_path_preservation(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_analysis.skpy:
import os
import sqlite3
from dedup_file_tools_fs_copy.phases.analysis import (
    persist_file_metadata,
    scan_file_on_directory,
    analyze_directories,
)
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def setup_test_db(tmp_path, table):
    pass


def test_persist_file_metadata_insert_and_update(tmp_path):
    pass


def test_scan_file_on_directory(tmp_path):
    pass


def test_analyze_directories(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_cli_config_yaml.skpy:
import os
import tempfile
import yaml
import subprocess
import sys
import pytest


def make_yaml_config(tmp_path, config_dict):
    pass


def run_cli_with_config(config_path, extra_args):
    pass


def test_invalid_yaml(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_cli_workflow_copy.skpy:
import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_fs_copy import main


def test_cli_workflow_copy(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_deep.skpy:
import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_fs_copy import main


def test_cli_workflow_verify_deep(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_cli_workflow_verify_shallow.skpy:
import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_fs_copy import main


def test_cli_workflow_verify_shallow(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_copy_with_destination_pool.skpy:
import tempfile
import shutil
import sqlite3
from pathlib import Path
import pytest
from dedup_file_tools_fs_copy import main


def test_copy_with_destination_pool(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_destination_pool_cache_validation.skpy:
import os
import sqlite3
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
import time


def setup_destination_pool_db(tmp_path):
    pass


def test_exists_at_destination_pool(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_destination_pool_cli.skpy:
from dedup_file_tools_fs_copy.utils.destination_pool_cli import (
    add_to_destination_index_pool,
)
from dedup_file_tools_fs_copy.utils.destination_pool import DestinationPoolIndex
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def test_add_to_destination_index_pool(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_destination_pool_index.skpy:
import sqlite3
from dedup_file_tools_fs_copy.utils.destination_pool import DestinationPoolIndex
from dedup_file_tools_commons.utils.uidpath import UidPathUtil


def setup_test_db(tmp_path):
    pass


def test_add_and_exists(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_generate_config.skpy:
import io
import os
import tempfile
import builtins
import pytest
from dedup_file_tools_fs_copy.main import main


def test_generate_config_interactive(monkeypatch):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_handle_resume.skpy:
import sqlite3
from pathlib import Path
from dedup_file_tools_fs_copy.main import (
    handle_init,
    handle_add_source,
    handle_resume,
    get_db_path_from_job_dir,
)


def test_handle_resume_integration(tmp_path):
    pass


def test_handle_resume_corrupted_and_missing(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_import_checksums.skpy:
import sqlite3
from dedup_file_tools_fs_copy import main
from dedup_file_tools_commons.utils.uidpath import UidPathUtil
import pytest


def test_import_checksums_from_other_db(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_one_shot_command.skpy:
import os
import pytest
from dedup_file_tools_fs_copy import main


def test_one_shot_minimal(tmp_path):
    pass


def test_one_shot_with_options(tmp_path):
    pass


==========.skpy-skeleton\tests\dedup_file_tools_fs_copy\test_summary.skpy:
import os
import sqlite3
import tempfile
import shutil
from dedup_file_tools_fs_copy.phases.summary import summary_phase


def setup_db_with_files(statuses):
    pass


def test_summary_all_done(tmp_path):
    pass


def test_summary_with_errors_and_pending(tmp_path):
    pass


## How to Use This Reference

- Use this outline to locate the relevant skeleton or source file for any feature or bugfix.
- Refer to the corresponding `.skpy` file for the function/class signatures and docstrings.
- For implementation details, see the mapped original Python files as listed in `SKELETON_MAPPING.md`.

---

_Last updated: 2025-07-21_
