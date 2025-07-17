# Implementation Note: Efficient File Move for dedup_file_tools_dupes_move

## Requirement
When moving duplicate files, always use the native `os.rename` (or `Path.rename`) function for moves within the same filesystem/drive. This ensures that moves are atomic and nearly instantaneous, as no data is copied—only directory entries are updated. This is critical for performance and correctness when moving large files on the same drive.

If the source and destination are on different filesystems/drives, fall back to a copy-and-delete approach, but always prefer the fast path when possible.

---

## Implementation Strategy
- Use `os.rename(src, dst)` or `Path(src).rename(dst)` for all moves.
- Before moving, check if `os.path.samefile(os.path.dirname(src), os.path.dirname(dst))` or use `os.stat(src).st_dev == os.stat(dst_dir).st_dev` to confirm both are on the same device.
- If on the same device, proceed with `rename`.
- If not, perform a copy (using `shutil.copy2` or similar), then delete the source file.
- Always handle exceptions and log the operation type (fast move vs. copy+delete).

---

## Example Code Snippet
```python
import os
import shutil
from pathlib import Path

def move_file(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Fast path: same device
        if os.stat(src_path).st_dev == os.stat(dst_path.parent).st_dev:
            src_path.rename(dst_path)
            return 'fast-move'
        else:
            shutil.copy2(src_path, dst_path)
            src_path.unlink()
            return 'copy-delete'
    except Exception as e:
        # Log and handle error
        raise
```

---

## Auditability
- Log whether each move was a fast (rename) or slow (copy+delete) operation.
- Record errors and fallbacks for troubleshooting.

---

## References
- Python docs: [`os.rename`](https://docs.python.org/3/library/os.html#os.rename), [`shutil.copy2`](https://docs.python.org/3/library/shutil.html#shutil.copy2)
- See also: `dedup_file_tools_commons.utils.fileops` for shared file operation utilities.
