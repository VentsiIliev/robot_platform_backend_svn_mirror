#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${APP_DIR}/.venv/bin/python"

# Bootstrap an independent environment for this checkout.
if [[ ! -x "${PYTHON}" ]]; then
  echo "Creating platform Python environment..."
  if ! "${PYTHON_BIN:-python3}" -m venv "${APP_DIR}/.venv"; then
    echo "Virtual environment creation failed. On Ubuntu install python3-venv, then retry." >&2
    exit 1
  fi
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
if ! "${PYTHON}" -c 'from PyQt6 import QtWidgets; import cv2; from pyzbar.pyzbar import decode'; then
  echo "Platform dependency check failed. Missing zbar on Ubuntu: sudo apt install libzbar0" >&2
  exit 1
fi
if [[ "${1:-}" == "--setup-only" ]]; then
  echo "Platform environment is ready."
  exit 0
fi
if [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--setup-only]" >&2
  exit 2
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

"${PYTHON}" "${APP_DIR}/src/bootstrap/run_main.py" &
APP_PID=$!
wait "${APP_PID}"
