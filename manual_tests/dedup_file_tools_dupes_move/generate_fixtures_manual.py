import os
import argparse

def generate_files(src, n=5):
    # Create subdirectories
    dir_a = os.path.join(src, "a")
    dir_b = os.path.join(src, "b")
    os.makedirs(dir_a, exist_ok=True)
    os.makedirs(dir_b, exist_ok=True)
    # Create unique files in a
    for i in range(n):
        with open(os.path.join(dir_a, f"file{i}.txt"), "w") as f:
            f.write(f"Test file {i} for dedup_file_tools_dupes_move\n")
    # Create a true duplicate in b (same content as file0.txt in a)
    with open(os.path.join(dir_b, "file0.txt"), "w") as f:
        f.write("Test file 0 for dedup_file_tools_dupes_move\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test files for dedup_file_tools_dupes_move manual tests.")
    parser.add_argument("--src", required=True, help="Directory to create test files in.")
    parser.add_argument("--n", type=int, default=5, help="Number of unique files to create (default: 5)")
    args = parser.parse_args()
    generate_files(args.src, args.n)
