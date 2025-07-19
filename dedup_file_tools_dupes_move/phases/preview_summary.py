import logging
from dedup_file_tools_commons.utils.robust_sqlite import RobustSqliteConn

def preview_summary(db_path):
    """
    Print a summary of planned duplicate moves and groups before any file operations.
    """
    with RobustSqliteConn(db_path).connect() as conn:
        cur = conn.cursor()
        # Count planned moves
        cur.execute("SELECT COUNT(*) FROM dedup_move_plan WHERE status='planned'")
        planned_count = cur.fetchone()[0]
        # Count duplicate groups
        cur.execute("SELECT COUNT(DISTINCT checksum) FROM dedup_move_plan WHERE status='planned'")
        group_count = cur.fetchone()[0]
        # Count keepers
        cur.execute("SELECT COUNT(*) FROM dedup_move_plan WHERE is_keeper=1")
        keeper_count = cur.fetchone()[0]
        # Print summary
        print("\n==== PREVIEW SUMMARY ====")
        print(f"Planned duplicate groups: {group_count}")
        print(f"Files to be moved: {planned_count}")
        print(f"Files to be kept (keepers): {keeper_count}")
        print("\nSample planned moves:")
        cur.execute("""
            SELECT uid, relative_path, checksum, move_to_uid, move_to_rel_path
            FROM dedup_move_plan WHERE status='planned' LIMIT 10
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  Move: {row[0]}:{row[1]} (checksum={row[2]}) -> {row[3]}:{row[4]}")
        if planned_count > 10:
            print(f"  ...and {planned_count-10} more planned moves.")
    logging.info("Previewed planned duplicate moves and groups.")
