"""
File: src/utils/fileops.py
Description: File operations utilities (copy, verify, etc.)
"""
import shutil
import hashlib
from pathlib import Path
from tqdm import tqdm
import os

def copy_file(src, dst, block_size=4096, progress_callback=None, show_progressbar=False):
    """Copy file from src to dst in blocks, with optional progress callback and per-file progressbar. Preserves mtime. File-level resume: always restarts file if interrupted."""
    total_size = Path(src).stat().st_size
    copied = 0
    if show_progressbar and total_size > 0:
        with tqdm(total=total_size, desc=f"Copying {Path(src).name}", unit="B", unit_scale=True, leave=False) as file_pbar:
            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                h_src = hashlib.sha256()
                h_dst = hashlib.sha256()
                while True:
                    buf = fsrc.read(block_size)
                    if not buf:
                        break
                    fdst.write(buf)
                    h_src.update(buf)
                    h_dst.update(buf)  # Since we just wrote, src==dst
                    copied += len(buf)
                    file_pbar.update(len(buf))
                    if progress_callback and total_size > 0:
                        percent = int((copied / total_size) * 100)
                        progress_callback(percent, copied, total_size)
    else:
        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
            h_src = hashlib.sha256()
            h_dst = hashlib.sha256()
            while True:
                buf = fsrc.read(block_size)
                if not buf:
                    break
                fdst.write(buf)
                h_src.update(buf)
                h_dst.update(buf)
                copied += len(buf)
                if progress_callback and total_size > 0:
                    percent = int((copied / total_size) * 100)
                    progress_callback(percent, copied, total_size)
    # Preserve mtime
    src_stat = Path(src).stat()
    os.utime(dst, (src_stat.st_atime, src_stat.st_mtime))
    # Return checksums for verification
    return h_src.hexdigest(), h_dst.hexdigest()

def verify_file(src, dst):
    """Verify that two files have the same SHA-256 checksum."""
    return compute_sha256(src) == compute_sha256(dst)

def compute_sha256(file_path, block_size=4096):
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()
