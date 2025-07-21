import os
import sqlite3
import tempfile
import shutil
from dedup_file_tools_commons.utils.checksum_cache2 import ChecksumCache2
from dedup_file_tools_commons.utils.uidpath import UidPathUtil

def test_exists_at_pool():
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, 'test.db')
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE left_pool_files (uid TEXT, relative_path TEXT, size INTEGER, last_modified INTEGER)')
        conn.execute('CREATE TABLE checksum_cache (uid TEXT, relative_path TEXT, size INTEGER, last_modified INTEGER, checksum TEXT, is_valid INTEGER, PRIMARY KEY(uid, relative_path))')
        # Insert file and checksum
        conn.execute('INSERT INTO left_pool_files VALUES (?, ?, ?, ?)', ('uid1', 'file1.txt', 3, 12345))
        conn.execute('INSERT INTO checksum_cache VALUES (?, ?, ?, ?, ?, ?, ?)', ('uid1', 'file1.txt', 3, 12345, 'abc123', 1))
        conn.commit()
        cc = ChecksumCache2(UidPathUtil())
        assert cc.exists_at_pool(conn, 'left_pool_files', 'abc123')
        assert not cc.exists_at_pool(conn, 'left_pool_files', 'notfound')
        print('ChecksumCache2.exists_at_pool test passed.')
    finally:
        shutil.rmtree(tmpdir)

if __name__ == '__main__':
    test_exists_at_pool()
