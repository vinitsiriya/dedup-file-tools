# UidPath: System-Independent Path Abstraction

The `UidPath` class provides a robust method to convert standard file paths into a system-independent format using a unique identifier (UID) for the filesystem and a relative path from the filesystem's mount point. This abstraction enables portable and consistent file referencing across different operating systems and environments.

> **Note:** On Windows, the UID is essentially a replacement for the drive letter (e.g., `C:`), but instead of using the drive letter, it uses the volume's serial number. This allows for more robust and portable file references, even if drive letters change.

> **Important:**
> - The `relative_path` returned by `convert_path` is only guaranteed to be relative to the detected mount point.
> - Its format may be long or look like an absolute path segment, especially in test/temp environments.
> - Only `UidPath` should interpret or manipulate `rel_path`; all other code should treat it as opaque.

## Key Components

- **UID (Unique Identifier):** Represents the filesystem. On Linux, this is the filesystem's UUID; on Windows, it is the volume's serial number (serving as a replacement for the drive letter).
- **Relative Path:** The path of the file relative to the mount point of the filesystem identified by the UID. Its format is only guaranteed to be relative to the detected mount point, and may be long or look absolute in some environments.

## Benefits

- **System Independence:** File paths are portable between different systems by abstracting away absolute paths and system-specific details.
- **Consistency:** Essential for scenarios like backups, restores, and deduplication across different machines where absolute paths may differ but the underlying filesystem and file structure remain the same.

## Supported Operations

- **Convert Path to UID/Relative Format:** Translates a standard file path into a tuple of (UID, relative path), making it portable and system-agnostic.
- **Reconstruct Path:** Given a UID and relative path, reconstructs the absolute path on the current system if the volume is available.

## Use Cases

- Backup and restore workflows
- Deduplication and checksum caching
- Cross-platform file management

## Example Usage

### Windows Example
Suppose you have a file at `C:\Users\Alice\Documents\report.docx` and the C: drive has a volume serial number `A1B2C3D4`.

```python
from dedup_file_tools_commons.utils.uidpath import UidPathUtil

uid_path = UidPathUtil()
uid, rel_path = uid_path.convert_path(r'C:\Users\Alice\Documents\report.docx')
# uid: 'A1B2C3D4' (the volume serial number for C:)
# rel_path: 'Users/Alice/Documents/report.docx' (relative to the root of C:\)

# To reconstruct the absolute path:
abs_path = uid_path.reconstruct_path(uid, rel_path)
# abs_path: Path('C:/Users/Alice/Documents/report.docx')
```

### Linux Example
Suppose you have a file at `/mnt/data/photos/image.jpg` and `/mnt/data` is a mount point with UUID `1234-ABCD`.

```python
from dedup_file_tools_commons.utils.uidpath import UidPathUtil

uid_path = UidPathUtil()
uid, rel_path = uid_path.convert_path('/mnt/data/photos/image.jpg')
# uid: '1234-ABCD' (the UUID for /mnt/data)
# rel_path: 'photos/image.jpg' (relative to /mnt/data)

# To reconstruct the absolute path:
abs_path = uid_path.reconstruct_path(uid, rel_path)
# abs_path: Path('/mnt/data/photos/image.jpg')
```

### Test/Temporary Directory Example
Suppose you have a test file at `C:\Temp\pytest-123\mount\file.txt` and `C:\Temp\pytest-123\mount` is treated as a pseudo-mount in tests.

```python
uid, rel_path = uid_path.convert_path(r'C:\Temp\pytest-123\mount\file.txt')
# uid: 'C:\Temp\pytest-123\mount' (the pseudo-mount path)
# rel_path: 'file.txt' (relative to the pseudo-mount)
```

This approach ensures that file references remain valid and portable, regardless of the underlying operating system or mount point changes.

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.
