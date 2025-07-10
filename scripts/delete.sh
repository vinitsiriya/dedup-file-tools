#!/usr/bin/env bash
# delete.sh: Remove obsolete files from src/ as per project protocol
# Review before running!

set -e

rm -f "$(dirname "$0")/../src/scan.py"
rm -f "$(dirname "$0")/../src/analysis.py"
rm -f "$(dirname "$0")/../src/checksum.py"

# Empty this script after successful execution as per protocol
: > "$(dirname "$0")/delete.sh"
