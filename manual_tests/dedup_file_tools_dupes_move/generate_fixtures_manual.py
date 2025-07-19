import os

def generate_files(pool_dir):
    dir_a = os.path.join(pool_dir, "a")
    dir_b = os.path.join(pool_dir, "b")
    os.makedirs(dir_a, exist_ok=True)
    os.makedirs(dir_b, exist_ok=True)
    # True duplicate
    with open(os.path.join(dir_a, "file0.txt"), "w") as f:
        f.write("hello")
    with open(os.path.join(dir_b, "file0.txt"), "w") as f:
        f.write("hello")
    # Unique files
    for i in range(1, 5):
        with open(os.path.join(dir_a, f"file{i}.txt"), "w") as f:
            f.write(f"unique{i}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", required=True, help="Directory to create pool files in")
    args = parser.parse_args()
    generate_files(args.pool)
