#!/usr/bin/env bash
set -euo pipefail

PROJECT_SLUG="linux-network-speed-indicator"
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
EXEC_PATH="${BIN_DIR}/${PROJECT_SLUG}"
DATA_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}"
SHARE_DIR="${DATA_HOME}/${PROJECT_SLUG}"
CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
CONFIG_DIR="${CONFIG_HOME}/${PROJECT_SLUG}"
APPLICATIONS_DIR="${DATA_HOME}/applications"
APPLICATION_DESKTOP_PATH="${APPLICATIONS_DIR}/${PROJECT_SLUG}.desktop"
ICON_THEME_DIR="${DATA_HOME}/icons/hicolor/scalable/apps"
APP_ICON_PATH="${ICON_THEME_DIR}/${PROJECT_SLUG}.svg"
METAINFO_DIR="${DATA_HOME}/metainfo"
METAINFO_PATH="${METAINFO_DIR}/io.github.MasumMSNR.LinuxNetworkSpeedIndicator.metainfo.xml"
AUTOSTART_DIR="${CONFIG_HOME}/autostart"
AUTOSTART_PATH="${AUTOSTART_DIR}/${PROJECT_SLUG}.desktop"

if ! command -v /usr/bin/python3 >/dev/null 2>&1; then
  echo "python3 is required." >&2
  exit 1
fi

if ! /usr/bin/python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('AyatanaAppIndicator3', '0.1')" >/dev/null 2>&1; then
  echo "Missing GTK/AppIndicator Python bindings." >&2
  echo "On Ubuntu/Debian install:" >&2
  echo "  sudo apt install python3 python3-gi gir1.2-ayatanaappindicator3-0.1 libayatana-appindicator3-1" >&2
  exit 1
fi

mkdir -p \
  "${BIN_DIR}" \
  "${SHARE_DIR}/icons" \
  "${CONFIG_DIR}" \
  "${AUTOSTART_DIR}" \
  "${APPLICATIONS_DIR}" \
  "${ICON_THEME_DIR}" \
  "${METAINFO_DIR}"

install -m 0755 "${PROJECT_ROOT}/src/network_speed_indicator.py" "${EXEC_PATH}"
install -m 0644 "${PROJECT_ROOT}/assets/icons/network-speed-indicator-empty.svg" "${SHARE_DIR}/icons/network-speed-indicator-empty.svg"
install -m 0644 "${PROJECT_ROOT}/assets/icons/linux-network-speed-indicator.svg" "${APP_ICON_PATH}"
install -m 0644 "${PROJECT_ROOT}/assets/metainfo/linux-network-speed-indicator.metainfo.xml" "${METAINFO_PATH}"
install -m 0644 "${PROJECT_ROOT}/config/default-config.json" "${SHARE_DIR}/default-config.json"

if [ ! -f "${CONFIG_DIR}/config.json" ]; then
  install -m 0644 "${PROJECT_ROOT}/config/default-config.json" "${CONFIG_DIR}/config.json"
fi

sed "s|__EXEC_PATH__|${EXEC_PATH}|g" \
  "${PROJECT_ROOT}/assets/applications/linux-network-speed-indicator.desktop.in" \
  > "${APPLICATION_DESKTOP_PATH}"
chmod 0644 "${APPLICATION_DESKTOP_PATH}"

sed "s|__EXEC_PATH__|${EXEC_PATH}|g" \
  "${PROJECT_ROOT}/assets/autostart/linux-network-speed-indicator.desktop.in" \
  > "${AUTOSTART_PATH}"
chmod 0644 "${AUTOSTART_PATH}"

if command -v desktop-file-validate >/dev/null 2>&1; then
  desktop-file-validate "${APPLICATION_DESKTOP_PATH}"
  desktop-file-validate "${AUTOSTART_PATH}"
fi

if command -v appstreamcli >/dev/null 2>&1; then
  appstreamcli validate --no-net "${METAINFO_PATH}"
fi

if [ -n "${DISPLAY:-}" ] && [ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
  pkill -f "${EXEC_PATH}" >/dev/null 2>&1 || true
  setsid -f env \
    DISPLAY="${DISPLAY}" \
    DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS}" \
    XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-}" \
    XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-}" \
    "${EXEC_PATH}" >/dev/null 2>&1 || true
fi

echo "Installed ${PROJECT_SLUG}."
echo "Binary: ${EXEC_PATH}"
echo "Config: ${CONFIG_DIR}/config.json"
echo "Launcher: ${APPLICATION_DESKTOP_PATH}"
echo "Autostart: ${AUTOSTART_PATH}"
echo "Icon: ${APP_ICON_PATH}"
echo "AppStream: ${METAINFO_PATH}"
