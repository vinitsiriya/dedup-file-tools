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
    copy_status TEXT,
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
    copy_status TEXT,
    error_message TEXT,
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_source_checksum ON source_files (checksum);
CREATE INDEX IF NOT EXISTS idx_dest_checksum ON destination_files (checksum);
CREATE INDEX IF NOT EXISTS idx_source_status ON source_files (copy_status);
'''

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
