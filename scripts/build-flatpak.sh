#!/usr/bin/env bash

set -euo pipefail

APP_ID="io.github.MasumMSNR.LinuxNetworkSpeedIndicator"
MANIFEST="${APP_ID}.yaml"
BRANCH="${FLATPAK_BRANCH:-stable}"
BUILD_DIR="${1:-dist/flatpak-build}"
REPO_DIR="${2:-dist/flatpak-repo}"
BUNDLE_PATH="${3:-dist/${APP_ID}.flatpak}"

if ! command -v flatpak >/dev/null 2>&1; then
  echo "flatpak is required" >&2
  exit 1
fi

if ! command -v flatpak-builder >/dev/null 2>&1; then
  echo "flatpak-builder is required" >&2
  echo "Install it with your distro package manager and rerun this script." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

mkdir -p "$(dirname "${BUILD_DIR}")" "$(dirname "${REPO_DIR}")" "$(dirname "${BUNDLE_PATH}")"

if ! flatpak remote-info flathub org.gnome.Platform//50 >/dev/null 2>&1; then
  flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
fi

flatpak-builder \
  --force-clean \
  --repo="${REPO_DIR}" \
  --install-deps-from=flathub \
  "${BUILD_DIR}" \
  "${MANIFEST}"

flatpak build-bundle "${REPO_DIR}" "${BUNDLE_PATH}" "${APP_ID}" "${BRANCH}"

echo "Built ${BUNDLE_PATH}"
echo "Install locally with: flatpak install --user ${BUNDLE_PATH}"
echo "Run with: flatpak run ${APP_ID}"