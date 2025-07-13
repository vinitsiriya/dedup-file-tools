#!/usr/bin/env python3
"""
generate_fixtures_manual.py

Generate simple, planned directory structures for manual testing.
Creates 'source' and 'dest' directories with predictable, human-readable contents.

Usage:
    python generate_fixtures_manual.py --src ./manual_src --dst ./manual_dst --depth 2 --width 3 --files 2
"""
import os
import argparse
from pathlib import Path
import shutil
import logging

def create_tree(root: Path, depth: int, width: int, files_per_folder: int, prefix: str = ""):
    if depth == 0:
        return
    for i in range(1, width + 1):
        folder = root / f"folder{i}"
        folder.mkdir(parents=True, exist_ok=True)
        for j in range(1, files_per_folder + 1):
            file_path = folder / f"file{j}.txt"
            file_path.write_text(f"This is {file_path}")
        # Recurse
        create_tree(folder, depth - 1, width, files_per_folder, prefix="")

def create_tree_with_dups(root: Path):
    """Create a clear deduplication test structure with descriptive names."""
    # Folder for duplicate content
    dups = root / "duplicates"
    dups.mkdir(parents=True, exist_ok=True)
    (dups / "dup_alpha.txt").write_text("DUPLICATE_CONTENT")
    (dups / "dup_beta.txt").write_text("DUPLICATE_CONTENT")
    # Folder for unique content
    uniques = root / "uniques"
    uniques.mkdir(parents=True, exist_ok=True)
    (uniques / "unique_1.txt").write_text("UNIQUE_CONTENT_1")
    (uniques / "unique_2.txt").write_text("UNIQUE_CONTENT_2")

def main():
    parser = argparse.ArgumentParser(description="Generate simple source and dest directory trees for manual testing.")
    parser.add_argument('--src', type=str, default='./manual_src', help='Source directory path')
    parser.add_argument('--dst', type=str, default='./manual_dst', help='Destination directory path')
    parser.add_argument('--depth', type=int, default=2, help='Depth of directory tree')
    parser.add_argument('--width', type=int, default=3, help='Number of folders per level')
    parser.add_argument('--files', type=int, default=2, help='Number of files per folder')
    parser.add_argument('--clean', action='store_true', help='Clean target directories before generating')
    args = parser.parse_args()

    for path in [args.src, args.dst]:
        p = Path(path)
        if args.clean and p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True, exist_ok=True)

    # Create source tree (no prefix for folders/files)
    create_tree(Path(args.src), args.depth, args.width, args.files, prefix="")
    # Create destination tree (empty or partial for manual copy/skip testing)
    create_tree(Path(args.dst), 1, 1, 0, prefix="dst_")  # Just a root folder, no files by default
    # Create source tree with clear dups and uniques for manual deduplication test
    create_tree_with_dups(Path(args.src))

    logging.basicConfig(level=logging.INFO)
    logging.debug(f"Source tree created at: {args.src}")
    logging.debug(f"Destination tree created at: {args.dst}")

if __name__ == "__main__":
    main()
