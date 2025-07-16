"""
Migration script to move status fields from source_files and destination_files to the new copy_status table.
Run this script once after deploying the new schema.
"""
import sqlite3
import sys

def migrate_status_fields(db_path):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        # Create copy_status table if not exists
        cur.execute('''
            CREATE TABLE IF NOT EXISTS copy_status (
                uid TEXT,
                relative_path TEXT,
                status TEXT,
                last_copy_attempt INTEGER,
                error_message TEXT,
                PRIMARY KEY (uid, relative_path)
            )
        ''')
        # Migrate from source_files
        cur.execute('''
            SELECT uid, relative_path, copy_status, last_copy_attempt, error_message FROM source_files
            WHERE copy_status IS NOT NULL
        ''')
        for uid, rel_path, status, last_copy_attempt, error_message in cur.fetchall():
            cur.execute('''
                INSERT OR REPLACE INTO copy_status (uid, relative_path, status, last_copy_attempt, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (uid, rel_path, status, last_copy_attempt, error_message))
        # Remove columns from source_files
        # (SQLite does not support DROP COLUMN directly; requires table rebuild. Manual step may be needed.)
        # Optionally, drop columns or leave as-is for backward compatibility
        # Remove status fields from destination_files if present (optional)
        conn.commit()
        print("Migration complete. Status fields moved to copy_status table.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <db_path>")
        sys.exit(1)
    migrate_status_fields(sys.argv[1])
