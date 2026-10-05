#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_WS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

resolve_ros_setup_file() {
  if [[ -n "${ROS_SETUP_FILE:-}" ]]; then
    printf '%s\n' "${ROS_SETUP_FILE}"
    return
  fi
  if [[ -n "${ROS_DISTRO:-}" && -f "/opt/ros/${ROS_DISTRO}/setup.bash" ]]; then
    printf '/opt/ros/%s/setup.bash\n' "${ROS_DISTRO}"
    return
  fi
  if [[ -f /opt/ros/rolling/setup.bash ]]; then
    printf '%s\n' /opt/ros/rolling/setup.bash
    return
  fi
  if [[ -f /opt/ros/jazzy/setup.bash ]]; then
    printf '%s\n' /opt/ros/jazzy/setup.bash
    return
  fi
  return 1
}

source_setup() {
  local file="$1"
  local had_u=0
  if [[ $- == *u* ]]; then
    had_u=1
    set +u
  fi
  # shellcheck disable=SC1090
  source "${file}"
  if [[ ${had_u} -eq 1 ]]; then
    set -u
  fi
}

ROS_SETUP="$(resolve_ros_setup_file)" || {
  echo "No ROS setup file found. Set ROS_SETUP_FILE=/opt/ros/<distro>/setup.bash" >&2
  exit 1
}

# Prevent a terminal that previously sourced another distro/overlay from leaking
# paths into this build.
unset AMENT_PREFIX_PATH COLCON_PREFIX_PATH CMAKE_PREFIX_PATH ROS_PACKAGE_PATH
unset PYTHONPATH
unset ROS_DISTRO ROS_VERSION ROS_PYTHON_VERSION

source_setup "${ROS_SETUP}"

if [[ -n "${MOVEIT_SETUP_FILE:-}" ]]; then
  if [[ ! -f "${MOVEIT_SETUP_FILE}" ]]; then
    echo "MOVEIT_SETUP_FILE not found: ${MOVEIT_SETUP_FILE}" >&2
    exit 1
  fi
  source_setup "${MOVEIT_SETUP_FILE}"
fi

# Always include dependencies: a failed build can leave local_setup.bash behind.
# Dependency integration tests are opt-in; backend unit tests use test_backend.sh.
BUILD_TESTING="${BUILD_TESTING:-OFF}"
case "${BUILD_TESTING}" in
  ON|OFF) ;;
  *) echo "BUILD_TESTING must be ON or OFF" >&2; exit 2 ;;
esac
printf 'Building ZeroErr with ROS %s (BUILD_TESTING=%s)\n' "${ROS_DISTRO}" "${BUILD_TESTING}"
cd "${ROOT_WS_DIR}"
colcon build --symlink-install --packages-up-to erob_moveit_runtime zeroerr \
  --cmake-args -DCMAKE_BUILD_TYPE=Release "-DBUILD_TESTING=${BUILD_TESTING}"
