import os
import logging
from dedup_file_tools_commons.db import init_checksum_db
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def connect_with_attached_checksum_db(main_db_path, checksum_db_path):
    """
    Ensure the checksum DB exists and has the correct schema, then attach it to the main DB connection as 'checksumdb'.
    Returns a sqlite3.Connection object with the checksum DB attached.
    """
    # Ensure attached checksum DB has correct schema
    if not os.path.exists(checksum_db_path):
        init_checksum_db(checksum_db_path)
    else:
        # Try to create missing tables/indexes if DB exists but is incomplete
        try:
            init_checksum_db(checksum_db_path)
        except Exception as e:
            logging.error(f"Failed to ensure schema in attached checksum DB: {checksum_db_path}\nError: {e}")
            raise
    conn = RobustSqliteConn(main_db_path).connect()
    # Attach checksum DB as 'checksumdb'
    conn.execute(f"ATTACH DATABASE '{checksum_db_path}' AS checksumdb")
    return conn
