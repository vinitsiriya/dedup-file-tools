"""
db.py: SQLite schema management for Non-Redundant Media File Copy Tool
"""
import sqlite3

SCHEMA = '''
CREATE TABLE IF NOT EXISTS source_files (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    checksum TEXT,
    checksum_stale INTEGER,
    copy_status TEXT, -- 'pending', 'in_progress', 'done', 'error'
    last_copy_attempt INTEGER,
    error_message TEXT,
    PRIMARY KEY (uid, relative_path)
);
CREATE TABLE IF NOT EXISTS destination_files (
    uid TEXT,
    relative_path TEXT,
    last_modified INTEGER,
    size INTEGER,
    checksum TEXT,
    checksum_stale INTEGER,
    copy_status TEXT, -- 'pending', 'in_progress', 'done', 'error'
    error_message TEXT,
    PRIMARY KEY (uid, relative_path)
);
CREATE TABLE IF NOT EXISTS checksum_cache (
    uid TEXT,
    relative_path TEXT,
    checksum TEXT,
    source TEXT,
    imported_at INTEGER,
    PRIMARY KEY (uid, relative_path, source)
);
CREATE INDEX IF NOT EXISTS idx_source_checksum ON source_files (checksum);
CREATE INDEX IF NOT EXISTS idx_dest_checksum ON destination_files (checksum);
CREATE INDEX IF NOT EXISTS idx_source_status ON source_files (copy_status);

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
    PRIMARY KEY (uid, relative_path, timestamp)
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
    PRIMARY KEY (uid, relative_path, timestamp)
);
'''

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
