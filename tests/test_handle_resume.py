import sqlite3
from pathlib import Path
from fs_copy_tool.main import handle_init, handle_add_source, handle_resume, get_db_path_from_job_dir

def test_handle_resume_integration(tmp_path):
    # Setup: create job dir, src, dst
    job_dir = tmp_path / "job"
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    job_name = "testjob"
    src.mkdir()
    dst.mkdir()
    (src / "fileA.txt").write_text("A")
    (src / "fileB.txt").write_text("B")
    (src / "fileC.txt").write_text("C")

    # Step 1: Initialize job dir
    class Args: pass
    args_init = Args()
    args_init.job_dir = str(job_dir)
    args_init.job_name = job_name
    handle_init(args_init)

    # Step 2: Add source files to DB
    args_add = Args()
    args_add.job_dir = str(job_dir)
    args_add.job_name = job_name
    args_add.src = str(src)
    handle_add_source(args_add)

    # Step 3: Mark fileA as already copied
    db_path = get_db_path_from_job_dir(str(job_dir), job_name)
    relA = str(src / "fileA.txt")
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO copy_status (uid, relative_path, status, last_copy_attempt, error_message)
            SELECT uid, relative_path, 'done', 0, NULL FROM source_files WHERE relative_path=?
            ON CONFLICT(uid, relative_path) DO UPDATE SET status='done', last_copy_attempt=0, error_message=NULL
        """, (relA,))
        conn.commit()

    # Step 4: Call handle_resume
    args_resume = Args()
    args_resume.job_dir = str(job_dir)
    args_resume.job_name = job_name
    args_resume.src = [str(src)]
    args_resume.dst = [str(dst)]
    handle_resume(args_resume)

    # Step 5: Assert all files present in dst (at the tool's current output location)
    assert (dst / relA).read_text() == "A"
    assert (dst / str(src / "fileB.txt")).read_text() == "B"
    assert (dst / str(src / "fileC.txt")).read_text() == "C"

def test_handle_resume_corrupted_and_missing(tmp_path):
    from fs_copy_tool.main import handle_init, handle_add_source, handle_resume, get_db_path_from_job_dir
    import sqlite3

    job_dir = tmp_path / "job2"
    src = tmp_path / "src2"
    dst = tmp_path / "dst2"
    src.mkdir()
    dst.mkdir()
    (src / "fileA.txt").write_text("A")
    (src / "fileB.txt").write_text("B")
    (src / "fileC.txt").write_text("C")

    # Init and add source
    class Args: pass
    args_init = Args()
    job_name = "testjob"
    args_init.job_dir = str(job_dir)
    args_init.job_name = job_name
    handle_init(args_init)
    args_add = Args()
    args_add.job_dir = str(job_dir)
    args_add.job_name = job_name
    args_add.src = str(src)
    handle_add_source(args_add)

    db_path = get_db_path_from_job_dir(str(job_dir), job_name)
    relA = str(src / "fileA.txt")
    relB = str(src / "fileB.txt")
    relC = str(src / "fileC.txt")

    # Simulate: fileA is already copied and correct, fileB is present but corrupted, fileC is missing
    (dst / relA).parent.mkdir(parents=True, exist_ok=True)
    (dst / relA).write_text("A")  # correct
    (dst / relB).parent.mkdir(parents=True, exist_ok=True)
    (dst / relB).write_text("CORRUPT")  # corrupted
    # fileC is missing

    # Mark fileA and fileB as done, fileC as pending
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for rel, status in [(relA, 'done'), (relB, 'done'), (relC, 'pending')]:
            cur.execute("""
                INSERT INTO copy_status (uid, relative_path, status, last_copy_attempt, error_message)
                SELECT uid, relative_path, ?, 0, NULL FROM source_files WHERE relative_path=?
                ON CONFLICT(uid, relative_path) DO UPDATE SET status=?, last_copy_attempt=0, error_message=NULL
            """, (status, rel, status,))
        conn.commit()

    # Resume
    args_resume = Args()
    args_resume.job_dir = str(job_dir)
    args_resume.job_name = job_name
    args_resume.src = [str(src)]
    args_resume.dst = [str(dst)]
    handle_resume(args_resume)

    # Assert: fileA is unchanged, fileB is still corrupted (not fixed by resume), fileC is present
    assert (dst / relA).read_text() == "A"
    assert (dst / relB).read_text() == "CORRUPT"  # not fixed, as per current logic
    assert (dst / relC).read_text() == "C"
