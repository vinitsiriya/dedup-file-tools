#!/usr/bin/env bash
# test.sh: Run all Python tests using pytest
set -e
.venv/bin/python -m pytest --maxfail=3 --disable-warnings -v
