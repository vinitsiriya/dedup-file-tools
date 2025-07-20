from dedup_file_tools_commons.utils.paths import get_db_path_from_job_dir, get_checksum_db_path
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn
from dedup_file_tools_commons.utils.checksum_cache import ChecksumCache
from dedup_file_tools_commons.utils.uidpath import UidPathUtil, UidPath
from tqdm import tqdm
import logging

def ensure_destination_pool_checksums(job_dir, job_name, checksum_db=None):
    db_path = get_db_path_from_job_dir(job_dir, job_name)
    checksum_db_path = get_checksum_db_path(job_dir, checksum_db)
    from dedup_file_tools_fs_copy.db import init_db
    from dedup_file_tools_commons.utils.db_utils import connect_with_attached_checksum_db
    init_db(db_path)
    def conn_factory():
        return connect_with_attached_checksum_db(db_path, checksum_db_path)
    checksum_cache = ChecksumCache(conn_factory, UidPathUtil())
    # Get all files in the destination pool
    with conn_factory() as conn:
        cur = conn.cursor()
        cur.execute("SELECT uid, relative_path FROM destination_pool_files")
        pool_files = cur.fetchall()
    if pool_files:
        from concurrent.futures import ThreadPoolExecutor
        from threading import Lock
        pbar_lock = Lock()
        uid_path = UidPathUtil()
        def process_pool_file(args):
            uid, rel_path = args
            uid_path_obj = UidPath(uid, rel_path)
            abs_path = uid_path.reconstruct_path(uid_path_obj)
            if abs_path is None:
                logging.warning(f"[COPY][POOL] Skipping file: could not reconstruct path for uid={uid}, rel_path={rel_path}")
                return
            checksum_cache.get_or_compute_with_invalidation(abs_path)
            with pbar_lock:
                pbar.update(1)
        with tqdm(total=len(pool_files), desc="Updating pool checksums") as pbar:
            with ThreadPoolExecutor() as executor:
                list(executor.map(process_pool_file, pool_files))
