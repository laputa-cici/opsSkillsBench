#!/bin/bash
set -euo pipefail

python -m pytest /tests/test_outputs.py -rA

