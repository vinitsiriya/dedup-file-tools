#!/usr/bin/env bash
# lint.sh: Run flake8 linter
set -e
flake8 src/ tests/
