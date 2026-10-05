#!/usr/bin/env bash
set -euo pipefail
PLATFORM_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PLATFORM_PROJECT_ROOT"
ROBOT_DEPLOYMENT_SCRIPT="$PLATFORM_PROJECT_ROOT/../deployment/scripts/manage_robot.py"
if [[ -f "$ROBOT_DEPLOYMENT_SCRIPT" ]]; then
    exec /usr/bin/python3 -B "$ROBOT_DEPLOYMENT_SCRIPT" install glue "$@"
fi
exec /usr/bin/python3 "$PLATFORM_PROJECT_ROOT/packaging/platform/local_release.py" install glue "$@"
