import os
import argparse

def generate_files(src, n=5):
    os.makedirs(src, exist_ok=True)
    for i in range(n):
        with open(os.path.join(src, f"dupes_move_file{i}.txt"), "w") as f:
            f.write(f"Test file {i} for dedup_file_tools_dupes_move\n")
    # Add a duplicate
    if n > 1:
        with open(os.path.join(src, f"dupes_move_file0_copy.txt"), "w") as f:
            f.write("Test file 0 for dedup_file_tools_dupes_move\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test files for dedup_file_tools_dupes_move manual tests.")
    parser.add_argument("--src", required=True, help="Directory to create test files in.")
    parser.add_argument("--n", type=int, default=5, help="Number of unique files to create (default: 5)")
    args = parser.parse_args()
    generate_files(args.src, args.n)
