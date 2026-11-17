#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[run.sh] Using python: $($PYTHON_BIN --version)"
echo "[run.sh] Starting pilot: kospi-information-diet-vs-reasoning-scaffold"

"$PYTHON_BIN" run_pilot.py --config config.yaml "$@"
