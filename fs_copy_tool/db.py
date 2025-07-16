CHECKSUM_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS checksum_cache (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    imported_at INTEGER,
    last_validated INTEGER,
    is_valid INTEGER DEFAULT 1, -- 1=valid, 0=stale
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_checksum_cache_uid_relpath ON checksum_cache(uid, relative_path);
CREATE INDEX IF NOT EXISTS idx_checksum_cache_checksum_valid ON checksum_cache(checksum, is_valid);
"""

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

CHECKSUM_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS checksum_cache (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    imported_at INTEGER,
    last_validated INTEGER,
    is_valid INTEGER DEFAULT 1, -- 1=valid, 0=stale
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_checksum_cache_uid_relpath ON checksum_cache(uid, relative_path);
CREATE INDEX IF NOT EXISTS idx_checksum_cache_checksum_valid ON checksum_cache(checksum, is_valid);
"""


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()

def init_checksum_db(checksum_db_path):
    conn = sqlite3.connect(checksum_db_path)
    try:
        conn.executescript(CHECKSUM_DB_SCHEMA)
        conn.commit()
    finally:
        conn.close()
