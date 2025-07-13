"""
Fixture Generator Script for fs-copy-tool

Generates large, complex, and edge-case file/directory structures for E2E and stress testing.
Usage:
    python scripts/generate_fixtures.py --output <dir> [--size <N>] [--depth <N>] [--large-files] [--many-files] ...

See README or script docstring for all options.
"""
import os
import sys
import argparse
from pathlib import Path

# ...existing code for argument parsing and fixture generation will go here...

def main():
    parser = argparse.ArgumentParser(description="Generate test fixtures for fs-copy-tool.")
    parser.add_argument('--output', required=True, help='Output directory for fixtures')
    parser.add_argument('--size', type=int, default=100, help='Number of files (default: 100)')
    parser.add_argument('--depth', type=int, default=3, help='Directory depth (default: 3)')
    parser.add_argument('--large-files', action='store_true', help='Include large files')
    parser.add_argument('--many-files', action='store_true', help='Create many small files')
    parser.add_argument('--verbose', action='store_true', help='Show verbose output')
    # Add more arguments for other edge cases as needed
    args = parser.parse_args()

    outdir = Path(args.output)
    outdir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Generating fixtures in {outdir} ...")
    print(f"[INFO] Directory depth: {args.depth}, Files per dir: {args.size}")
    if args.large_files:
        print("[INFO] Large files enabled.")
    if args.many_files:
        print("[INFO] Many small files enabled.")

    total_files = 0
    total_large = 0
    total_dot = 0
    total_future = 0
    total_past = 0
    total_special = 0
    total_dup = 0
    # Example: create nested directories
    for d in range(args.depth):
        nested = outdir / ("nested_" * (d+1))
        nested.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Creating files in {nested} ...")
        for i in range(args.size):
            long_name = f"file_{i}_" + ("x" * 100) + ".txt" if i % 10 == 0 else f"file_{i}.txt"
            f = nested / long_name
            with open(f, 'w') as fh:
                fh.write(f"Test file {i} at depth {d}\n")
            total_files += 1
            if args.large_files and i % 20 == 0:
                large_f = nested / f"large_file_{i}.bin"
                with open(large_f, 'wb') as fh:
                    fh.write(os.urandom(10 * 1024 * 1024))  # 10MB
                total_large += 1
            if i % 15 == 0:
                dotfile = nested / f".hidden_{i}"
                with open(dotfile, 'w') as fh:
                    fh.write("Hidden file\n")
                total_dot += 1
            if i % 25 == 0:
                future_file = nested / f"future_{i}.txt"
                with open(future_file, 'w') as fh:
                    fh.write("Future timestamp\n")
                os.utime(future_file, (32503680000, 32503680000))  # Year 3000
                total_future += 1
            if i % 30 == 0:
                past_file = nested / f"past_{i}.txt"
                with open(past_file, 'w') as fh:
                    fh.write("Past timestamp\n")
                os.utime(past_file, (0, 0))  # Epoch
                total_past += 1
            if i % 12 == 0:
                special = nested / f"spécial_文件_{i}.txt"
                with open(special, 'w', encoding='utf-8') as fh:
                    fh.write("Unicode filename\n")
                total_special += 1
        if args.size > 1:
            dup1 = nested / "dup1.txt"
            dup2 = nested / "dup2.txt"
            with open(dup1, 'w') as fh:
                fh.write("duplicate content\n")
            with open(dup2, 'w') as fh:
                fh.write("duplicate content\n")
            total_dup += 2
    if args.many_files:
        print(f"[INFO] Creating many small files in {outdir} ...")
        for i in range(1000):  # Reduced from 10000 to 1000 for faster tests
            f = outdir / f"tiny_{i}.txt"
            with open(f, 'w') as fh:
                fh.write("x\n")
            total_files += 1
            if args.verbose and i % 200 == 0:
                print(f"[INFO] Created {i} tiny files...")
    # TODO: Add logic for read-only files, sparse files, symlinks/hard links, permissions, and identical names in different dirs.
    print("[SUMMARY] Fixture generation complete.")
    print(f"[SUMMARY] Total files: {total_files}")
    print(f"[SUMMARY] Large files: {total_large}, Dotfiles: {total_dot}, Future: {total_future}, Past: {total_past}, Special: {total_special}, Duplicates: {total_dup}")
    print(f"[SUMMARY] Output directory: {outdir}")

if __name__ == "__main__":
    main()
