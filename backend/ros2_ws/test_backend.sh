#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if ! /usr/bin/python3 -m pytest --version >/dev/null 2>&1; then
  echo "Missing pytest. Install with: sudo apt install python3-pytest" >&2
  exit 1
fi
cd "${SCRIPT_DIR}"
exec /usr/bin/python3 -m pytest \
  eRob_moveit/src/eRob_ROS2_MoveIt/erob_moveit_runtime/test/ -q "$@"
