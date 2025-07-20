import sqlite3
from dedup_file_tools_fs_copy.utils.destination_pool import DestinationPoolIndex
from dedup_file_tools_commons.utils.uidpath import UidPathUtil

def setup_test_db(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE destination_pool_files (
            uid TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            size INTEGER,
            last_modified INTEGER,
            last_seen INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    """)
    conn.commit()
    conn.close()
    return str(db_path)

def test_add_and_exists(tmp_path):
    import sqlite3
    db_path = setup_test_db(tmp_path)
    uid_path = UidPathUtil()
    pool = DestinationPoolIndex(uid_path)
    # Create a temp file
    file_path = tmp_path / "file1.txt"
    file_path.write_text("hello world")
    stat = file_path.stat()
    with sqlite3.connect(db_path) as conn:
        pool.add_or_update_file(conn, str(file_path), stat.st_size, int(stat.st_mtime))
        uid_path_obj = uid_path.convert_path(str(file_path))
        uid, rel = uid_path_obj.uid, uid_path_obj.relative_path
        assert pool.exists(conn, uid, str(rel))
        # Should not exist for a different file
        assert not pool.exists(conn, uid, "not_a_file.txt")
