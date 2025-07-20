
from dedup_file_tools_fs_copy.utils.destination_pool_cli import add_to_destination_index_pool
from dedup_file_tools_fs_copy.utils.destination_pool import DestinationPoolIndex
from dedup_file_tools_commons.utils.uidpath import UidPathUtil

def test_add_to_destination_index_pool(tmp_path):
    db_path = tmp_path / "test.db"
    # Create the destination_pool_files table
    import sqlite3
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
    # Create a destination root with files
    dst_root = tmp_path / "dst"
    dst_root.mkdir()
    file1 = dst_root / "file1.txt"
    file2 = dst_root / "file2.txt"
    file1.write_text("foo")
    file2.write_text("bar")
    # Run the CLI logic
    add_to_destination_index_pool(str(db_path), str(dst_root))
    # Check that both files are in the pool index
    import sqlite3
    uid_path = UidPathUtil()
    pool = DestinationPoolIndex(uid_path)
    uid_path_obj1 = uid_path.convert_path(str(file1))
    uid1, rel1 = uid_path_obj1.uid, uid_path_obj1.relative_path
    uid_path_obj2 = uid_path.convert_path(str(file2))
    uid2, rel2 = uid_path_obj2.uid, uid_path_obj2.relative_path
    with sqlite3.connect(db_path) as conn:
        assert pool.exists(conn, uid1, str(rel1))
        assert pool.exists(conn, uid2, str(rel2))
