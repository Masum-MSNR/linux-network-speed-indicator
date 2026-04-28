#!/usr/bin/env bash
set -euo pipefail

PROJECT_SLUG="linux-network-speed-indicator"
EXEC_PATH="${HOME}/.local/bin/${PROJECT_SLUG}"
DATA_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}"
SHARE_DIR="${DATA_HOME}/${PROJECT_SLUG}"
APPLICATION_DESKTOP_PATH="${DATA_HOME}/applications/${PROJECT_SLUG}.desktop"
CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
CONFIG_DIR="${CONFIG_HOME}/${PROJECT_SLUG}"
AUTOSTART_PATH="${CONFIG_HOME}/autostart/${PROJECT_SLUG}.desktop"
PURGE_CONFIG=false

if [ "${1:-}" = "--purge" ]; then
  PURGE_CONFIG=true
elif [ -n "${1:-}" ]; then
  echo "Usage: ./uninstall.sh [--purge]" >&2
  exit 1
fi

pkill -f "${EXEC_PATH}" >/dev/null 2>&1 || true
rm -f "${EXEC_PATH}"
rm -f "${AUTOSTART_PATH}"
rm -f "${APPLICATION_DESKTOP_PATH}"
rm -rf "${SHARE_DIR}"

if [ "${PURGE_CONFIG}" = true ]; then
  rm -rf "${CONFIG_DIR}"
  echo "Removed application files and user configuration."
else
  echo "Removed application files. User configuration kept at ${CONFIG_DIR}."
  echo "Run ./uninstall.sh --purge if you also want to remove settings."
fi
