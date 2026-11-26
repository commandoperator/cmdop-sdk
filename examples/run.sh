#!/usr/bin/env bash
# Inventory owns selection/effects. ONLY never grants permission; no owner-token fallback.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$HERE/runner.py" "$@"
