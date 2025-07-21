import os

def generate_files(left_dir, right_dir):
    os.makedirs(left_dir, exist_ok=True)
    os.makedirs(right_dir, exist_ok=True)
    # Identical file
    with open(os.path.join(left_dir, "file0.txt"), "w") as f:
        f.write("hello")
    with open(os.path.join(right_dir, "file0.txt"), "w") as f:
        f.write("hello")
    # Unique to left
    for i in range(1, 3):
        with open(os.path.join(left_dir, f"file{i}.txt"), "w") as f:
            f.write(f"left_unique_{i}")
    # Unique to right
    for i in range(1, 3):
        with open(os.path.join(right_dir, f"file{i+2}.txt"), "w") as f:
            f.write(f"right_unique_{i}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--left", required=True, help="Directory to create left files in")
    parser.add_argument("--right", required=True, help="Directory to create right files in")
    args = parser.parse_args()
    generate_files(args.left, args.right)
