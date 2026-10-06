#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${APP_DIR}/.venv/bin/python"

if [[ $# -gt 1 || ( $# -eq 1 && "${1}" != "--setup-only" ) ]]; then
  echo "Usage: $0 [--setup-only]" >&2
  exit 2
fi

# Bootstrap an independent environment for this checkout.
if [[ ! -x "${PYTHON}" ]]; then
  echo "Creating platform Python environment..."
  if ! "${PYTHON_BIN:-python3}" -m venv "${APP_DIR}/.venv"; then
    echo "Virtual environment creation failed. On Ubuntu install python3-venv, then retry." >&2
    exit 1
  fi
fi

# Native libraries are OS dependencies and are not supplied by pip.
NATIVE_PACKAGES=()
for dependency in 'zbar:libzbar.so.0:libzbar0' 'xcb-cursor:libxcb-cursor.so.0:libxcb-cursor0'; do
  IFS=: read -r library soname package <<< "${dependency}"
  if ! env -u PYTHONPATH "${PYTHON}" -c 'import ctypes, ctypes.util, sys; ctypes.CDLL(ctypes.util.find_library(sys.argv[1]) or sys.argv[2])' "${library}" "${soname}" 2>/dev/null; then
    NATIVE_PACKAGES+=("${package}")
  fi
done
if [[ ${#NATIVE_PACKAGES[@]} -gt 0 ]]; then
  if [[ ! -f /etc/os-release ]]; then
    echo "Missing native dependencies: ${NATIVE_PACKAGES[*]}. Install them for your operating system, then retry." >&2
    exit 1
  fi
  source /etc/os-release
  if [[ "${ID:-}" != "ubuntu" && "${ID:-}" != "debian" ]]; then
    echo "Missing native dependencies: ${NATIVE_PACKAGES[*]}. Install them for your operating system, then retry." >&2
    exit 1
  fi
  echo "Installing missing system dependencies: ${NATIVE_PACKAGES[*]} (administrator access required)..."
  APT_COMMAND=(apt-get)
  if [[ "${EUID}" -ne 0 ]]; then
    if ! command -v sudo >/dev/null; then
      echo "Ask an administrator to install ${NATIVE_PACKAGES[*]}, then retry." >&2
      exit 1
    fi
    APT_COMMAND=(sudo apt-get)
  fi
  "${APT_COMMAND[@]}" update
  "${APT_COMMAND[@]}" install -y "${NATIVE_PACKAGES[@]}"
fi

REQUIREMENTS="${APP_DIR}/requirements.txt"
STAMP="${APP_DIR}/.venv/.platform-requirements.sha256"
REQUIREMENTS_HASH="$(sha256sum "${REQUIREMENTS}" | cut -d ' ' -f 1)"
INSTALLED_HASH=""
[[ ! -f "${STAMP}" ]] || INSTALLED_HASH="$(cat "${STAMP}")"
if [[ "${INSTALLED_HASH}" != "${REQUIREMENTS_HASH}" ]]; then
  echo "Installing platform dependencies (first setup or changed requirements)..."
  env -u PYTHONPATH "${PYTHON}" -m pip install -r "${REQUIREMENTS}"
  env -u PYTHONPATH "${PYTHON}" -m pip check
  printf '%s\n' "${REQUIREMENTS_HASH}" > "${STAMP}"
fi

# Verify native and GUI imports without starting application or robot services.
if ! env -u PYTHONPATH "${PYTHON}" -c 'from PyQt6 import QtWidgets; import cv2; from pyzbar.pyzbar import decode'; then
  echo "Platform dependency check failed. See the import error above for the failing dependency." >&2
  exit 1
fi
if [[ "${1:-}" == "--setup-only" ]]; then
  echo "Platform environment is ready."
  exit 0
fi

export PYTHONPATH="${APP_DIR}:${PYTHONPATH:-}"
cd "${APP_DIR}"

ORIGINAL_STTY=""
APP_PID=""

if [[ -t 0 ]]; then
  ORIGINAL_STTY="$(stty -g)"
  stty intr ^X
  echo "Press Ctrl+X in this terminal to stop the robot app."
fi

cleanup() {
  local status=$?
  trap - INT TERM HUP EXIT

  if [[ -n "${APP_PID}" ]] && kill -0 "${APP_PID}" 2>/dev/null; then
    kill -INT "${APP_PID}" 2>/dev/null || true
    for _ in {1..300}; do
      kill -0 "${APP_PID}" 2>/dev/null || break
      sleep 0.1
    done
    if kill -0 "${APP_PID}" 2>/dev/null; then
      kill -TERM "${APP_PID}" 2>/dev/null || true
    fi
    wait "${APP_PID}" 2>/dev/null || true
  fi

  if [[ -n "${ORIGINAL_STTY}" ]]; then
    stty "${ORIGINAL_STTY}" 2>/dev/null || true
  fi

  exit "${status}"
}

trap cleanup INT TERM HUP EXIT

"${PYTHON}" "${APP_DIR}/scripts/run_platform.py" &
APP_PID=$!
wait "${APP_PID}"
