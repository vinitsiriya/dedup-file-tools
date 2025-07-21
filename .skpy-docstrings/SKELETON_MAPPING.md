# Skeleton Directory Skip/Mapping Guide

This directory contains skeleton files generated from the original Python source files.

## How to Use
- Each `.skpy` file here is a skeleton version of a real Python file from your codebase.
- The original location of each file is recorded below.
- Use this mapping to find the source file for any skeleton.

**Source root:** `<source_root>`

**Skeleton output root:** `<skeleton_output_root>`

> The table below maps each generated skeleton file (left column) to its original Python source file (right column). All paths are relative to their respective root directories listed above. Use this mapping to trace any skeleton back to its source.

## Skeleton File Mapping

| Skeleton File | Original Source File |
|--------------|---------------------|
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
