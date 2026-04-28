#!/usr/bin/env bash
set -euo pipefail

PROJECT_SLUG="linux-network-speed-indicator"
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-$(cat "${PROJECT_ROOT}/VERSION")}"
ARCH="all"
DIST_DIR="${PROJECT_ROOT}/dist"
STAGING_DIR="${DIST_DIR}/${PROJECT_SLUG}_${VERSION}_${ARCH}"
DEB_PATH="${DIST_DIR}/${PROJECT_SLUG}_${VERSION}_${ARCH}.deb"

rm -rf "${STAGING_DIR}" "${DEB_PATH}"
mkdir -p \
  "${STAGING_DIR}/DEBIAN" \
  "${STAGING_DIR}/usr/bin" \
  "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps" \
  "${STAGING_DIR}/usr/share/metainfo" \
  "${STAGING_DIR}/usr/share/${PROJECT_SLUG}/icons" \
  "${STAGING_DIR}/usr/share/applications" \
  "${STAGING_DIR}/usr/share/doc/${PROJECT_SLUG}" \
  "${STAGING_DIR}/etc/xdg/autostart"

install -m 0755 "${PROJECT_ROOT}/src/network_speed_indicator.py" \
  "${STAGING_DIR}/usr/bin/${PROJECT_SLUG}"
install -m 0644 "${PROJECT_ROOT}/assets/icons/network-speed-indicator-empty.svg" \
  "${STAGING_DIR}/usr/share/${PROJECT_SLUG}/icons/network-speed-indicator-empty.svg"
install -m 0644 "${PROJECT_ROOT}/assets/icons/linux-network-speed-indicator.svg" \
  "${STAGING_DIR}/usr/share/icons/hicolor/scalable/apps/${PROJECT_SLUG}.svg"
install -m 0644 "${PROJECT_ROOT}/assets/metainfo/linux-network-speed-indicator.metainfo.xml" \
  "${STAGING_DIR}/usr/share/metainfo/io.github.MasumMSNR.LinuxNetworkSpeedIndicator.metainfo.xml"
install -m 0644 "${PROJECT_ROOT}/config/default-config.json" \
  "${STAGING_DIR}/usr/share/${PROJECT_SLUG}/default-config.json"
install -m 0644 "${PROJECT_ROOT}/README.md" \
  "${STAGING_DIR}/usr/share/doc/${PROJECT_SLUG}/README.md"
install -m 0644 "${PROJECT_ROOT}/CHANGELOG.md" \
  "${STAGING_DIR}/usr/share/doc/${PROJECT_SLUG}/CHANGELOG.md"
install -m 0644 "${PROJECT_ROOT}/LICENSE" \
  "${STAGING_DIR}/usr/share/doc/${PROJECT_SLUG}/copyright"

sed "s|__EXEC_PATH__|/usr/bin/${PROJECT_SLUG}|g" \
  "${PROJECT_ROOT}/assets/applications/linux-network-speed-indicator.desktop.in" \
  > "${STAGING_DIR}/usr/share/applications/${PROJECT_SLUG}.desktop"

sed "s|__EXEC_PATH__|/usr/bin/${PROJECT_SLUG}|g" \
  "${PROJECT_ROOT}/assets/autostart/linux-network-speed-indicator.desktop.in" \
  > "${STAGING_DIR}/etc/xdg/autostart/${PROJECT_SLUG}.desktop"

if command -v desktop-file-validate >/dev/null 2>&1; then
  desktop-file-validate "${STAGING_DIR}/usr/share/applications/${PROJECT_SLUG}.desktop"
  desktop-file-validate "${STAGING_DIR}/etc/xdg/autostart/${PROJECT_SLUG}.desktop"
fi

if command -v appstreamcli >/dev/null 2>&1; then
  appstreamcli validate --no-net "${STAGING_DIR}/usr/share/metainfo/io.github.MasumMSNR.LinuxNetworkSpeedIndicator.metainfo.xml"
fi

cat > "${STAGING_DIR}/DEBIAN/control" <<EOF
Package: ${PROJECT_SLUG}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: Masum
Depends: python3, python3-gi, gir1.2-ayatanaappindicator3-0.1, libayatana-appindicator3-1
Homepage: https://github.com/Masum-MSNR/${PROJECT_SLUG}
Description: Network speed indicator for Ubuntu GNOME and AppIndicator desktops
 Linux Network Speed Indicator is a lightweight top-bar and tray speed meter
 for Ubuntu GNOME and other Linux desktops that support AppIndicator or
 StatusNotifier items. It provides live download and upload speed, persistent
 settings, and autostart support.
EOF

cat > "${STAGING_DIR}/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi

exit 0
EOF

cat > "${STAGING_DIR}/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database /usr/share/applications >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q /usr/share/icons/hicolor >/dev/null 2>&1 || true
fi

exit 0
EOF

chmod 0755 "${STAGING_DIR}/DEBIAN/postinst" "${STAGING_DIR}/DEBIAN/postrm"

dpkg-deb --build --root-owner-group "${STAGING_DIR}" "${DEB_PATH}"

echo "Created ${DEB_PATH}"