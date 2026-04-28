#!/usr/bin/env bash
set -euo pipefail

PROJECT_SLUG="linux-network-speed-indicator"
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-$(cat "${PROJECT_ROOT}/VERSION")}"
DIST_DIR="${PROJECT_ROOT}/dist"
STAGING_DIR="${DIST_DIR}/${PROJECT_SLUG}-${VERSION}"
ARCHIVE_BASE="${DIST_DIR}/${PROJECT_SLUG}-${VERSION}"

rm -rf "${STAGING_DIR}" "${ARCHIVE_BASE}.zip" "${ARCHIVE_BASE}.tar.gz"
mkdir -p "${DIST_DIR}" "${STAGING_DIR}"

cp "${PROJECT_ROOT}/README.md" "${STAGING_DIR}/README.md"
cp "${PROJECT_ROOT}/LICENSE" "${STAGING_DIR}/LICENSE"
cp "${PROJECT_ROOT}/CHANGELOG.md" "${STAGING_DIR}/CHANGELOG.md"
cp "${PROJECT_ROOT}/VERSION" "${STAGING_DIR}/VERSION"
cp "${PROJECT_ROOT}/install.sh" "${STAGING_DIR}/install.sh"
cp "${PROJECT_ROOT}/uninstall.sh" "${STAGING_DIR}/uninstall.sh"
cp -R "${PROJECT_ROOT}/src" "${STAGING_DIR}/src"
cp -R "${PROJECT_ROOT}/assets" "${STAGING_DIR}/assets"
cp -R "${PROJECT_ROOT}/config" "${STAGING_DIR}/config"
cp -R "${PROJECT_ROOT}/scripts" "${STAGING_DIR}/scripts"

chmod +x "${STAGING_DIR}/install.sh" "${STAGING_DIR}/uninstall.sh" "${STAGING_DIR}/scripts/build-release.sh"

tar -C "${DIST_DIR}" -czf "${ARCHIVE_BASE}.tar.gz" "${PROJECT_SLUG}-${VERSION}"
(
  cd "${DIST_DIR}"
  zip -qr "${PROJECT_SLUG}-${VERSION}.zip" "${PROJECT_SLUG}-${VERSION}"
)

if command -v dpkg-deb >/dev/null 2>&1; then
  chmod +x "${PROJECT_ROOT}/scripts/build-deb.sh"
  "${PROJECT_ROOT}/scripts/build-deb.sh" "${VERSION}"
fi

echo "Created ${ARCHIVE_BASE}.tar.gz"
echo "Created ${ARCHIVE_BASE}.zip"
