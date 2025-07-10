#!/usr/bin/env bash
# archive_agents.sh: Archive all agent .md files to a date-stamped backup directory and reset them
set -e
BACKUP_DIR="agents/backup/$(date +%Y-%m-%d-%H%M)"
mkdir -p "$BACKUP_DIR"
for f in agents/*.md; do
  [ "$f" = "agents/backup" ] && continue
  cp "$f" "$BACKUP_DIR/"
  echo "# $(basename "$f")\n" > "$f"
done
