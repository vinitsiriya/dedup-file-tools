
import sqlite3
import os

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Pool tables (no checksum column; checksums are managed in commons db)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS left_pool_files (
            uid TEXT,
            relative_path TEXT,
            last_modified INTEGER,
            size INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS right_pool_files (
            uid TEXT,
            relative_path TEXT,
            last_modified INTEGER,
            size INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    ''')

    # Comparison results: files missing from right (present in left, not in right)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS compare_results_right_missing (
            uid TEXT,
            relative_path TEXT,
            last_modified INTEGER,
            size INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    ''')
    # Comparison results: files missing from left (present in right, not in left)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS compare_results_left_missing (
            uid TEXT,
            relative_path TEXT,
            last_modified INTEGER,
            size INTEGER,
            PRIMARY KEY (uid, relative_path)
        )
    ''')

    # Indexes for fast lookup
    cur.execute('CREATE INDEX IF NOT EXISTS idx_left_pool_uid_relpath ON left_pool_files(uid, relative_path)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_right_pool_uid_relpath ON right_pool_files(uid, relative_path)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_right_missing_uid_relpath ON compare_results_right_missing(uid, relative_path)')
    cur.execute('CREATE INDEX IF NOT EXISTS idx_left_missing_uid_relpath ON compare_results_left_missing(uid, relative_path)')

    conn.commit()
    conn.close()
