#!/usr/bin/env sh
set -eu

# Project-boundary PermissionRequest hook wrapper.
# Exit 0 approves the request; exit 1 falls through to Claude Code.

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
HELPER="$SCRIPT_DIR/safe-bash-permission.py"

if command -v python >/dev/null 2>&1; then
  exec python "$HELPER"
elif command -v python3 >/dev/null 2>&1; then
  exec python3 "$HELPER"
elif command -v py >/dev/null 2>&1; then
  exec py -3 "$HELPER"
fi

exit 1
