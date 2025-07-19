

# 🚀 dedup-file-tools: The Ultimate Toolkit for Safe, Fast, and Auditable File Management

**Two powerful CLI tools, one mission: never lose a file, never copy a duplicate, and always know what happened.**

---

## What Does Each Tool Do?

- **dedup-file-copy-fs**: Effortlessly copy files from one place to another—guaranteeing that only a single, non-duplicate copy of each file ever lands in your destination. No more wasted space or accidental double copies!

- **dedup-file-move-dupes**: Hunts down duplicate files in any folder or storage pool and safely moves all detected duplicates to a special `.dupes` directory. It’s the easiest way to clean up your drives and reclaim space—exciting, right?

Both tools are designed for safety, auditability, and total peace of mind!


## Why dedup-file-tools?

- **No more accidental duplicates:** Move or copy files between drives, folders, or backup pools with confidence—deduplication is automatic.
- **Resumable & robust:** Interrupt a job? No problem. All state is tracked in a job database. Resume anytime, anywhere.
- **Audit everything:** Every action, every file, every error—fully logged and queryable.
- **Cross-platform:** Works on Windows, Linux, and with both fixed and removable drives.
- **Portable & future-proof:** Thanks to UidPath, your job and checksum cache remain valid even if drive letters or mount points change.
- **Agent/AI ready:** YAML config, one-shot workflows, and full audit trails make it perfect for automation and integration.

---


## Two Tools, Two Workflows — Pick Your Power!

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
   Or, for a local development install:
   ```
   pip install .
   ```
2. **Generate a config file (recommended):**
   ```
   dedup-file-copy-fs generate-config
   # or
   dedup-file-move-dupes --config config.yaml
   ```
3. **Run a one-shot workflow:**
   ```
   dedup-file-move-dupes one-shot --job-dir ./myjob --job-name myjob --lookup-pool ./data --dupes-folder ./dupes
   dedup-file-copy-fs one-shot --job-dir ./copyjob --job-name copyjob --src ./source --dst ./dest
   ```
4. **Check logs, verify, and audit:**
   ```
   dedup-file-move-dupes summary --job-dir ./myjob --job-name myjob
   dedup-file-copy-fs verify --job-dir ./copyjob --job-name copyjob --stage deep
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
  - [dedup_file_tools_dupes_move CLI Reference](docs/dedup_file_tools_dupes_move/developer_reference/cli.md)
  - [dedup_file_tools_fs_copy CLI Reference](docs/dedup_file_tools_fs_copy/developer_reference/cli.md)
- **User guides & tutorials:**
  - [dedup_file_tools_dupes_move User Guide](docs/dedup_file_tools_dupes_move/user_prespective/README.md)
  - [dedup_file_tools_fs_copy User Guide](docs/dedup_file_tools_fs_copy/user_prepective/readme.md)
- **Agent/AI integration:**
  - [External AI Tool Integration](docs/dedup_file_tools_fs_copy/standalone/external_ai_tool_doc.md)
- **Requirements & design:**
  - [Requirements & Design](docs/dedup_file_tools_fs_copy/developer_reference/requirements/requirements.md)

---

## License
MIT License
