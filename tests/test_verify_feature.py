import shutil
from fs_copy_tool import main
def test_full_workflow_then_internal_verify(tmp_path):
    job_dir = tmp_path / "job"
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()
    # Create files in source
    (src_dir / "file1.txt").write_text("hello world")
    (src_dir / "file2.txt").write_text("deep verify test")

    # 1. Init job
    args = main.parse_args(["init", "--job-dir", str(job_dir)])
    assert main.run_main_command(args) == 0

    # 2. Analyze source and destination
    args = main.parse_args(["analyze", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir)])
    assert main.run_main_command(args) == 0

    # 3. Checksum source
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--table", "source_files"])
    assert main.run_main_command(args) == 0

    # 4. Checksum destination (should be empty at first)
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--table", "destination_files"])
    assert main.run_main_command(args) == 0

    # 5. Copy files
    args = main.parse_args(["copy", "--job-dir", str(job_dir), "--src", str(src_dir), "--dst", str(dst_dir), "--threads", "2"])
    assert main.run_main_command(args) == 0

    # 6. Checksum destination (after copy)
    args = main.parse_args(["checksum", "--job-dir", str(job_dir), "--table", "destination_files"])
    assert main.run_main_command(args) == 0

    from fs_copy_tool.phases.verify import verify_files
    db_path = job_dir / "copytool.db"
    # Run shallow verification
    verify_files(str(db_path), [str(src_dir)], [str(dst_dir)], stage='shallow')
    import sqlite3
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, verify_status FROM verification_shallow_results")
        shallow_results = {row[1]: (row[0], row[2]) for row in cur.fetchall()}
    print("Shallow verification results:", shallow_results)
    found_file1 = [k for k in shallow_results.keys() if k.endswith("file1.txt")]
    found_file2 = [k for k in shallow_results.keys() if k.endswith("file2.txt")]
    assert found_file1, f"file1.txt not found in shallow verification results: {shallow_results}"
    assert found_file2, f"file2.txt not found in shallow verification results: {shallow_results}"
    assert shallow_results[found_file1[0]][1] == "ok"
    assert shallow_results[found_file2[0]][1] == "ok"

    # Run deep verification
    verify_files(str(db_path), [str(src_dir)], [str(dst_dir)], stage='deep')
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path, verify_status, checksum_matched FROM verification_deep_results")
        deep_results = {row[1]: (row[0], row[2], row[3]) for row in cur.fetchall()}
    print("Deep verification results:", deep_results)
    # Print UID and relative_path for debugging
    for rel_path, (uid, status, matched) in deep_results.items():
        print(f"UID: {uid}, Relative Path: {rel_path}, Status: {status}, Checksum Matched: {matched}")
    # Accept both 'file1.txt' and possible subdir paths
    found_file1 = [k for k in deep_results.keys() if k.endswith("file1.txt")]
    found_file2 = [k for k in deep_results.keys() if k.endswith("file2.txt")]
    assert found_file1, f"file1.txt not found in deep verification results: {deep_results}"
    assert found_file2, f"file2.txt not found in deep verification results: {deep_results}"
