
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

DEDUPE_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS dedup_files_pool (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    scanned_at INTEGER,
    pool_base_path TEXT,
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_dedup_files_pool_checksum ON dedup_files_pool(checksum);

CREATE TABLE IF NOT EXISTS dedup_move_plan (
    uid TEXT,
    relative_path TEXT,
    checksum TEXT,
    move_to_uid TEXT,
    move_to_rel_path TEXT,
    status TEXT,
    error_message TEXT,
    planned_at INTEGER,
    moved_at INTEGER,
    updated_at INTEGER,
    is_keeper INTEGER DEFAULT 0,
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_dedup_move_plan_checksum ON dedup_move_plan(checksum);
CREATE INDEX IF NOT EXISTS idx_dedup_move_plan_status ON dedup_move_plan(status);
CREATE INDEX IF NOT EXISTS idx_dedup_move_plan_move_to ON dedup_move_plan(move_to_uid, move_to_rel_path);

CREATE TABLE IF NOT EXISTS dedup_move_history (
    uid TEXT,
    relative_path TEXT,
    attempted_at INTEGER,
    action TEXT,
    result TEXT,
    error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_dedup_move_history_attempted_at ON dedup_move_history(attempted_at);

CREATE TABLE IF NOT EXISTS dedup_job_meta (
    job_id TEXT PRIMARY KEY,
    job_name TEXT,
    created_at INTEGER,
    config_json TEXT,
    status TEXT,
    completed_at INTEGER
);

CREATE TABLE IF NOT EXISTS dedup_group_summary (
    checksum TEXT PRIMARY KEY,
    num_files INTEGER,
    keeper_uid TEXT,
    keeper_rel_path TEXT,
    group_status TEXT
);
"""


def init_db(db_path):
    conn = RobustSqliteConn(db_path).connect()
    try:
        conn.executescript(DEDUPE_DB_SCHEMA)
        # Migration: add pool_base_path if missing
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(dedup_files_pool);")
        columns = [row[1] for row in cur.fetchall()]
        if 'pool_base_path' not in columns:
            cur.execute("ALTER TABLE dedup_files_pool ADD COLUMN pool_base_path TEXT;")
            conn.commit()
    finally:
        conn.close()


DEDUPE_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS dedup_files_pool (
    uid TEXT,
    relative_path TEXT,
    size INTEGER,
    last_modified INTEGER,
    checksum TEXT,
    scanned_at INTEGER,
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_dedup_files_pool_checksum ON dedup_files_pool(checksum);

CREATE TABLE IF NOT EXISTS dedup_move_plan (
    uid TEXT,
    relative_path TEXT,
    checksum TEXT,
    move_to_uid TEXT,
    move_to_rel_path TEXT,
    status TEXT,
    error_message TEXT,
    planned_at INTEGER,
    moved_at INTEGER,
    updated_at INTEGER,
    is_keeper INTEGER DEFAULT 0,
    PRIMARY KEY (uid, relative_path)
);
CREATE INDEX IF NOT EXISTS idx_dedup_move_plan_checksum ON dedup_move_plan(checksum);
CREATE INDEX IF NOT EXISTS idx_dedup_move_plan_status ON dedup_move_plan(status);
CREATE INDEX IF NOT EXISTS idx_dedup_move_plan_move_to ON dedup_move_plan(move_to_uid, move_to_rel_path);

CREATE TABLE IF NOT EXISTS dedup_move_history (
    uid TEXT,
    relative_path TEXT,
    attempted_at INTEGER,
    action TEXT,
    result TEXT,
    error_message TEXT
);
CREATE INDEX IF NOT EXISTS idx_dedup_move_history_attempted_at ON dedup_move_history(attempted_at);

CREATE TABLE IF NOT EXISTS dedup_job_meta (
    job_id TEXT PRIMARY KEY,
    job_name TEXT,
    created_at INTEGER,
    config_json TEXT,
    status TEXT,
    completed_at INTEGER
);

CREATE TABLE IF NOT EXISTS dedup_group_summary (
    checksum TEXT PRIMARY KEY,
    num_files INTEGER,
    keeper_uid TEXT,
    keeper_rel_path TEXT,
    group_status TEXT
);
"""

def init_dedupe_db(db_path):
    """
    Initialize all deduplication tables in the given database.
    """
    conn = RobustSqliteConn(db_path).connect()
    try:
        conn.executescript(DEDUPE_DB_SCHEMA)
        conn.commit()
    finally:
        conn.close()
