


# 🚀 dedup-file-tools: The Ultimate Toolkit for Safe, Fast, and Auditable File Management

**Three powerful CLI tools, one mission: never lose a file, never copy a duplicate, always know what happened, and now—never miss a difference!**

<br>
<b>✨ New! <code>dedup-file-compare</code>: Instantly spot every difference, missing file, or change between any two folders, drives, or backup pools. Lightning-fast, fully auditable, and designed for peace of mind. <span style="color: #00b894;">Perfect for backup verification, migration audits, and total confidence!</span></b>

---

## What Does Each Tool Do?

- **dedup-file-copy-fs**: Effortlessly copy files from one place to another—guaranteeing that only a single, non-duplicate copy of each file ever lands in your destination. No more wasted space or accidental double copies!

- **dedup-file-move-dupes**: Hunts down duplicate files in any folder or storage pool and safely moves all detected duplicates to a special `.dupes` directory. It’s the easiest way to clean up your drives and reclaim space—exciting, right?

- **dedup-file-compare**: The newest member of the family! Instantly compare two directories (or backup pools) by checksum, size, or modification time. Find missing, extra, or changed files with blazing speed and total auditability. Perfect for backup verification, migration audits, and peace of mind!

All tools are designed for safety, auditability, and total peace of mind!



## Why dedup-file-tools?

- **No more accidental duplicates:** Move or copy files between drives, folders, or backup pools with confidence—deduplication is automatic.
- **Never miss a difference:** Instantly spot missing, extra, or changed files between any two locations. Verify backups, audit migrations, and sleep easy!
- **Resumable & robust:** Interrupt a job? No problem. All state is tracked in a job database. Resume anytime, anywhere.
- **Audit everything:** Every action, every file, every error—fully logged and queryable.
- **Cross-platform:** Works on Windows, Linux, and with both fixed and removable drives.
- **Portable & future-proof:** Thanks to UidPath, your job and checksum cache remain valid even if drive letters or mount points change.
- **Agent/AI ready:** YAML config, one-shot workflows, and full audit trails make it perfect for automation and integration.

---



## Three Tools, Three Workflows — Pick Your Power!

---


### 🆚 dedup-file-compare: The "Spot Every Difference" Workflow

Want to know exactly what changed, what’s missing, or what’s extra between two folders, drives, or backup pools? <b>This is your digital X-ray!</b> <br>
<b>dedup-file-compare</b> is the ultimate tool for backup verification, migration audits, and total confidence in your data. <span style="color: #0984e3;">No more guessing—just instant, auditable answers!</span>

#### Step-by-Step Tutorial

1. **Initialize your compare job:**
   ```
   dedup-file-compare init --job-dir ./comparejob --job-name comparejob
   ```
2. **Add your left and right directories:**
   ```
   dedup-file-compare add-to-left --job-dir ./comparejob --job-name comparejob --dir ./left
   dedup-file-compare add-to-right --job-dir ./comparejob --job-name comparejob --dir ./right
   ```
3. **Find missing, extra, or changed files:**
   ```
   dedup-file-compare find-missing-files --job-dir ./comparejob --job-name comparejob
   ```
4. **Show results, audit, and export:**
   ```
   dedup-file-compare show-result --job-dir ./comparejob --job-name comparejob --summary
   dedup-file-compare show-result --job-dir ./comparejob --job-name comparejob --output results.csv
   ```

<b>Want it all in one go?</b>
Just run:
```
dedup-file-compare one-shot --job-dir ./comparejob --job-name comparejob --left ./left --right ./right
```
<b>And... Voila! Instantly see every difference, missing file, or change—fully auditable and exportable. <span style="color: #00b894;">Sleep easy knowing your data is safe!</span></b>

See the [User Guide](docs/dedup_file_tools_compare/developer_reference/user_prepective/README.md) for advanced workflows and YAML config power.

---

### 🚦 dedup-file-copy-fs: The "Copy Without Duplicates" Workflow

Want to copy your files from one drive or folder to another, but never want to see a duplicate again? This is your magic wand!

#### Step-by-Step Tutorial

1. **Initialize your copy job:**
   ```
   dedup-file-copy-fs init --job-dir ./copyjob --job-name copyjob
   ```
2. **Add your source(s):**
   ```
   dedup-file-copy-fs add-source --job-dir ./copyjob --job-name copyjob --src ./source
   ```
3. **Analyze and checksum:**
   ```
   dedup-file-copy-fs analyze --job-dir ./copyjob --job-name copyjob --src ./source --dst ./dest
   dedup-file-copy-fs checksum --job-dir ./copyjob --job-name copyjob --table source_files
   dedup-file-copy-fs checksum --job-dir ./copyjob --job-name copyjob --table destination_files
   ```
4. **Copy, with deduplication magic:**
   ```
   dedup-file-copy-fs copy --job-dir ./copyjob --job-name copyjob --src ./source --dst ./dest
   ```
   Voila! Only unique files are copied. No duplicates, ever.
5. **Verify and audit:**
   ```
   dedup-file-copy-fs verify --job-dir ./copyjob --job-name copyjob --stage deep
   dedup-file-copy-fs log --job-dir ./copyjob
   ```

**Want it all in one go?**
Just run:
```
dedup-file-copy-fs one-shot --job-dir ./copyjob --job-name copyjob --src ./source --dst ./dest
```
And... Voila! Your files are safely, uniquely copied.

See the [User Guide](docs/dedup_file_tools_fs_copy/user_prepective/readme.md) for advanced tricks and YAML config magic.

---

### 🧹 dedup-file-move-dupes: The "Find & Sweep Duplicates" Workflow

Ready to reclaim space and banish duplicate files from your drives? This tool is your digital broom!

#### Step-by-Step Tutorial

1. **Initialize your dedupe job:**
   ```
   dedup-file-move-dupes init --job-dir ./myjob --job-name myjob
   ```
2. **Scan your pool for duplicates:**
   ```
   dedup-file-move-dupes analyze --job-dir ./myjob --job-name myjob --lookup-pool ./data
   dedup-file-move-dupes checksum --job-dir ./myjob --job-name myjob --table lookup_files
   ```
3. **Move all detected duplicates to .dupes:**
   ```
   dedup-file-move-dupes move-dupes --job-dir ./myjob --job-name myjob --dupes-folder ./dupes
   ```
   Voila! All your duplicate files are safely moved to `.dupes` for review or deletion.
4. **Summarize and audit:**
   ```
   dedup-file-move-dupes summary --job-dir ./myjob --job-name myjob
   dedup-file-move-dupes log --job-dir ./myjob
   ```

**Want it all in one go?**
Just run:
```
dedup-file-move-dupes one-shot --job-dir ./myjob --job-name myjob --lookup-pool ./data --dupes-folder ./dupes
```
And... Voila! Your drives are clean and duplicate-free.

See the [User Guide](docs/dedup_file_tools_dupes_move/user_prespective/README.md) for advanced workflows and YAML config power.

---


## Quick Start (Unified)

1. **Install (Recommended):**
   ```
   pipx install dedup-file-tools
   ```
   Or, to always get the latest version:
   ```
   pipx install dedup-file-tools
   ```
   Or, for a local development install:
   ```
   pip install .
   ```
2. **Generate a config file (recommended):**
   ```
   dedup-file-copy-fs generate-config
   # or
   dedup-file-move-dupes --config config.yaml
   # or
   dedup-file-compare --config config.yaml
   ```
3. **Run a one-shot workflow:**
   ```
   dedup-file-move-dupes one-shot --job-dir ./myjob --job-name myjob --lookup-pool ./data --dupes-folder ./dupes
   dedup-file-copy-fs one-shot --job-dir ./copyjob --job-name copyjob --src ./source --dst ./dest
   dedup-file-compare one-shot --job-dir ./comparejob --job-name comparejob --left ./left --right ./right
   ```
4. **Check logs, verify, and audit:**
   ```
   dedup-file-move-dupes summary --job-dir ./myjob --job-name myjob
   dedup-file-copy-fs verify --job-dir ./copyjob --job-name copyjob --stage deep
   dedup-file-compare show-result --job-dir ./comparejob --job-name comparejob --summary
   ```

---

## The Magic of UidPath

Both tools use a unique, system-independent path abstraction called **UidPath**. This means:
- Your job and checksum cache remain valid even if drive letters or mount points change.
- You can move drives between systems, plug into different USB ports, and never lose track of your files.
- Deduplication and verification are robust and portable.
See [UidPath documentation](docs/dedup_file_tools_commons/uidpath.md) for details.

---


## Want More?

- **Full CLI docs:**
  - [dedup_file_tools_compare CLI Reference](docs/dedup_file_tools_compare/developer_reference/user_prepective/cli.md)
  - [dedup_file_tools_dupes_move CLI Reference](docs/dedup_file_tools_dupes_move/developer_reference/cli.md)
  - [dedup_file_tools_fs_copy CLI Reference](docs/dedup_file_tools_fs_copy/developer_reference/cli.md)
- **User guides & tutorials:**
  - [dedup_file_tools_compare User Guide](docs/dedup_file_tools_compare/developer_reference/user_prepective/README.md)
  - [dedup_file_tools_dupes_move User Guide](docs/dedup_file_tools_dupes_move/user_prespective/README.md)
  - [Generic Tutorial: Move Duplicates (dedup-file-move-dupes)](docs/dedup_file_tools_dupes_move/user_prespective/generic_dupes_move_tutorial.md)
  - [dedup_file_tools_fs_copy User Guide](docs/dedup_file_tools_fs_copy/user_prepective/readme.md)
  - [Generic Tutorial: Copy Without Duplicates (dedup-file-copy-fs)](docs/dedup_file_tools_fs_copy/user_prepective/generic_copy_tutorial.md)
- **Agent/AI integration:**
  - [External AI Tool Integration (dedup-file-compare)](docs/dedup_file_tools_compare/standalone/external_ai_tool_doc.md)
  - [External AI Tool Integration (dedup-file-copy-fs)](docs/dedup_file_tools_fs_copy/standalone/external_ai_tool_doc.md)
  - [External AI Tool Integration (dedup-file-move-dupes)](docs/dedup_file_tools_dupes_move/standalone/external_ai_tool_doc.md)
- **Requirements & design:**
  - [Requirements & Design (dedup-file-compare)](docs/dedup_file_tools_compare/developer_reference/requirements/requirements.md)
  - [Requirements & Design (dedup-file-copy-fs)](docs/dedup_file_tools_fs_copy/developer_reference/requirements/requirements.md)
  - [Requirements & Design (dedup-file-move-dupes)](docs/dedup_file_tools_dupes_move/developer_reference/requirements/requirements.md)

---

## License
MIT License
