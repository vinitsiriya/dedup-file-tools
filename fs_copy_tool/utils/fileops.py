"""
File: src/utils/fileops.py
Description: File operations utilities (copy, verify, etc.)
"""
import shutil
import hashlib
from pathlib import Path

def copy_file(src, dst, block_size=4096):
    """Copy file from src to dst in blocks."""
    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        while True:
            buf = fsrc.read(block_size)
            if not buf:
                break
            fdst.write(buf)

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
