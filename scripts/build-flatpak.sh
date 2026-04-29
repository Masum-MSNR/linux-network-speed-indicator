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

if command -v flatpak-builder >/dev/null 2>&1; then
  BUILDER_MODE="host"
  FLATPAK_BUILDER=(flatpak-builder)
elif flatpak info --user org.flatpak.Builder >/dev/null 2>&1 || flatpak info org.flatpak.Builder >/dev/null 2>&1; then
  BUILDER_MODE="runtime"
  FLATPAK_BUILDER=(flatpak run --command=flathub-build org.flatpak.Builder)
else
  echo "flatpak-builder is required" >&2
  echo "Install it with your distro package manager or run: flatpak install --user flathub org.flatpak.Builder" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

mkdir -p "$(dirname "${BUILD_DIR}")" "$(dirname "${REPO_DIR}")" "$(dirname "${BUNDLE_PATH}")"

if ! flatpak remote-info flathub org.gnome.Platform//50 >/dev/null 2>&1; then
  flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
fi

rm -rf "${BUILD_DIR}" "${REPO_DIR}" "${BUNDLE_PATH}"

if [ "${BUILDER_MODE}" = "host" ]; then
  "${FLATPAK_BUILDER[@]}" \
    --disable-rofiles-fuse \
    --force-clean \
    --repo="${REPO_DIR}" \
    --install-deps-from=flathub \
    "${BUILD_DIR}" \
    "${MANIFEST}"
else
  WORK_DIR="$(mktemp -d)"
  trap 'rm -rf "${WORK_DIR}"' EXIT

  flatpak run \
    --cwd="${WORK_DIR}" \
    --filesystem="${WORK_DIR}" \
    --filesystem="${REPO_ROOT}:ro" \
    --command=flathub-build \
    org.flatpak.Builder \
    --disable-rofiles-fuse \
    "${REPO_ROOT}/${MANIFEST}"

  mv "${WORK_DIR}/builddir" "${BUILD_DIR}"
  mv "${WORK_DIR}/repo" "${REPO_DIR}"
fi

flatpak build-bundle "${REPO_DIR}" "${BUNDLE_PATH}" "${APP_ID}" "${BRANCH}"

echo "Built ${BUNDLE_PATH}"
echo "Install locally with: flatpak install --user ${BUNDLE_PATH}"
echo "Run with: flatpak run ${APP_ID}"