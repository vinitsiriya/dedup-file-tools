
"""
db.py: SQLite schema management for Non-Redundant Media File Copy Tool
"""
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

SCHEMA = '''
CREATE TABLE IF NOT EXISTS source_files (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    PRIMARY KEY (uid, relative_path)
);
CREATE TABLE IF NOT EXISTS destination_files (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    PRIMARY KEY (uid, relative_path)
);
CREATE TABLE IF NOT EXISTS copy_status (
    uid TEXT,
    relative_path TEXT,
    status TEXT, -- 'pending', 'in_progress', 'done', 'error'
    last_copy_attempt INTEGER,
    error_message TEXT,
    PRIMARY KEY (uid, relative_path)
);

-- Destination pool index (no checksums, just file presence)
CREATE TABLE IF NOT EXISTS destination_pool_files (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    last_seen INTEGER,
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_destination_pool_uid_relpath ON destination_pool_files(uid, relative_path);

-- Shallow verification results
CREATE TABLE IF NOT EXISTS verification_shallow_results (
    uid TEXT,
    relative_path TEXT,
    "exists" INTEGER,
    size_matched INTEGER,
    last_modified_matched INTEGER,
    expected_size INTEGER,
    actual_size INTEGER,
    expected_last_modified INTEGER,
    actual_last_modified INTEGER,
    verify_status TEXT,
    verify_error TEXT,
    timestamp INTEGER,
    PRIMARY KEY (uid, relative_path)
);

-- Deep verification results
CREATE TABLE IF NOT EXISTS verification_deep_results (
    uid TEXT,
    relative_path TEXT,
    checksum_matched INTEGER,
    expected_checksum TEXT,
    src_checksum TEXT,

    dst_checksum TEXT,
    verify_status TEXT,
    verify_error TEXT,
    timestamp INTEGER,
    PRIMARY KEY (uid, relative_path)
);
'''



def init_db(db_path):
    conn = RobustSqliteConn(db_path).connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

