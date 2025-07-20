# Tutorial: How to Copy Files Safely and Deduplicate with dedup-file-copy-fs

This guide explains, in plain English, how to use `dedup-file-copy-fs` to copy files from one location to another, ensuring you never copy duplicates and always have a full audit trail. The steps are suitable for any source and destination, and you can adapt them for your own drives, folders, or backup jobs.

## What You'll Need
- The `dedup-file-copy-fs` tool installed (see the main README for installation instructions)
- A source folder or drive (where your files are now)
- A destination folder or drive (where you want your files to go)
- (Optional) An existing checksum database for even faster deduplication

## Step-by-Step Instructions

### 1. Set Up Your Job
First, decide on a job directory and a job name. This is where all the state and logs will be kept. For example:
- Job directory: `./my_copy_job`
- Job name: `my_copy_job`

### 2. (Optional) Import Existing Checksums
If you have a checksum database from a previous job, you can import it to speed up deduplication. This step is optional but recommended for large or ongoing projects.

### 3. Add Your Source
Tell the tool where your source files are. This can be a folder, a drive, or even multiple locations.

### 4. Add Your Destination Index Pool
This step helps the tool know what files already exist at the destination, so it doesn't copy duplicates. Usually, you set this to the root of your destination drive or folder.

### 5. Analyze and Compute Checksums
The tool will scan both your source and destination, collecting information about all files. It then computes checksums (unique fingerprints) for every file, so it can detect duplicates with 100% accuracy.

### 6. Copy Files (Deduplication Magic!)
Now, run the copy command. Only files that don't already exist at the destination will be copied. If a job is interrupted, you can resume it at any time.

### 7. Verify and Audit
After copying, you can verify that every file was copied correctly. The tool supports both quick (shallow) and deep (checksum) verification. You can also check logs and summaries for a full audit trail.

## Example Commands (Replace with Your Own Paths)
```sh
# Initialize the job
dedup-file-copy-fs init --job-dir ./my_copy_job --job-name my_copy_job

# (Optional) Import checksums from another job
dedup-file-copy-fs import-checksums --job-dir ./my_copy_job --job-name my_copy_job --other-db ./other_job/checksum-cache.db

# Add your source
dedup-file-copy-fs add-source --job-dir ./my_copy_job --job-name my_copy_job --src /path/to/source

# Add your destination index pool
dedup-file-copy-fs add-to-destination-index-pool --job-dir ./my_copy_job --job-name my_copy_job --dst /path/to/destination

# Analyze and compute checksums
dedup-file-copy-fs analyze --job-dir ./my_copy_job --job-name my_copy_job --src /path/to/source --dst /path/to/destination
dedup-file-copy-fs checksum --job-dir ./my_copy_job --job-name my_copy_job --table source_files
dedup-file-copy-fs checksum --job-dir ./my_copy_job --job-name my_copy_job --table destination_files

# Copy files (deduplicated)
dedup-file-copy-fs copy --job-dir ./my_copy_job --job-name my_copy_job --src /path/to/source --dst /path/to/destination

# Verify and audit
dedup-file-copy-fs verify --job-dir ./my_copy_job --job-name my_copy_job --stage deep
dedup-file-copy-fs status --job-dir ./my_copy_job --job-name my_copy_job
```

## One-Shot: Do It All in One Command
If you want to run the whole workflow in a single step, use the `one-shot` command:
```sh
dedup-file-copy-fs one-shot --job-dir ./my_copy_job --job-name my_copy_job --src /path/to/source --dst /path/to/destination
```

## Tips
- You can use any folder or drive for source and destination—just update the paths.
- The tool is safe to resume if interrupted. Just rerun the same command.
- All actions are logged and auditable for peace of mind.
- For advanced options, see the main documentation.

---

This tutorial is designed to help anyone—no scripting required!—get started with safe, deduplicated file copying using dedup-file-copy-fs.
