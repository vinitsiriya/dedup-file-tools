import sqlite3
import time
from typing import Optional, Callable

class RobustSqliteConn:
    def __init__(self, db_path: str, timeout: float = 30.0, retries: int = 5, retry_delay: float = 0.5, wal: bool = True):
        self.db_path = db_path
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.wal = wal

    def connect(self) -> sqlite3.Connection:
        last_exc = None
        for attempt in range(self.retries):
            try:
                conn = sqlite3.connect(self.db_path, timeout=self.timeout, isolation_level=None)
                if self.wal:
                    conn.execute('PRAGMA journal_mode=WAL;')
                return conn
            except sqlite3.OperationalError as e:
                last_exc = e
                if 'database is locked' in str(e):
                    time.sleep(self.retry_delay)
                else:
                    raise
        raise last_exc

    def with_connection(self, fn: Callable[[sqlite3.Connection], None]):
        conn = self.connect()
        try:
            fn(conn)
        finally:
            conn.close()
