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

if ! flatpak remote-info --user flathub org.gnome.Platform//50 >/dev/null 2>&1; then
  flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
fi

rm -rf "${BUILD_DIR}" "${REPO_DIR}" "${BUNDLE_PATH}"

run_flatpak_builder() {
  if [ "${BUILDER_MODE}" = "host" ]; then
    status=0
    "${FLATPAK_BUILDER[@]}" \
      --user \
      --disable-rofiles-fuse \
      --force-clean \
      --repo="${REPO_DIR}" \
      --install-deps-from=flathub \
      "${BUILD_DIR}" \
      "${MANIFEST}" || status=$?
    return "${status}"
  fi

  work_dir="$(mktemp -d)"

  status=0
  flatpak run \
    --cwd="${work_dir}" \
    --filesystem="${work_dir}" \
    --filesystem="${REPO_ROOT}:ro" \
    --command=flathub-build \
    org.flatpak.Builder \
    --disable-rofiles-fuse \
    "${REPO_ROOT}/${MANIFEST}" || status=$?

  if [ "${status}" -eq 0 ]; then
    mv "${work_dir}/builddir" "${BUILD_DIR}"
    mv "${work_dir}/repo" "${REPO_DIR}"
    rm -rf "${work_dir}"
    return 0
  fi

  rm -rf "${work_dir}"
  return "${status}"
}

attempt=1
max_attempts="${FLATPAK_BUILD_RETRIES:-3}"

while :; do
  status=0
  run_flatpak_builder || status=$?

  if [ "${status}" -eq 0 ]; then
    break
  fi

  if [ "${attempt}" -ge "${max_attempts}" ]; then
    exit "${status}"
  fi

  echo "flatpak build failed on attempt ${attempt}/${max_attempts}; retrying after a transient download/build error..." >&2
  attempt=$((attempt + 1))
  rm -rf "${BUILD_DIR}" "${REPO_DIR}" "${BUNDLE_PATH}"
  sleep 5
done

flatpak build-bundle "${REPO_DIR}" "${BUNDLE_PATH}" "${APP_ID}" "${BRANCH}"

echo "Built ${BUNDLE_PATH}"
echo "Install locally with: flatpak install --user ${BUNDLE_PATH}"
echo "Run with: flatpak run ${APP_ID}"