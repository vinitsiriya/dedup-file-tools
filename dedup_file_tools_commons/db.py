"""
dedup_file_tools_commons/db.py
Checksum cache DB schema and initialization for shared use by all tools.
"""
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

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

CHECKSUM_DB_SCHEMA_ATTACHED = """
CREATE TABLE IF NOT EXISTS checksumdb.checksum_cache (
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
CREATE INDEX IF NOT EXISTS checksumdb.idx_checksum_cache_uid_relpath ON checksumdb.checksum_cache(uid, relative_path);
CREATE INDEX IF NOT EXISTS checksumdb.idx_checksum_cache_checksum_valid ON checksumdb.checksum_cache(checksum, is_valid);
"""

def init_checksum_db(checksum_db_path):
    conn = RobustSqliteConn(checksum_db_path).connect()
    try:
        conn.executescript(CHECKSUM_DB_SCHEMA)
        conn.commit()
    finally:
        conn.close()
