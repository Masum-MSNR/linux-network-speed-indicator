#!/usr/bin/env bash
set -euo pipefail

PROJECT_SLUG="linux-network-speed-indicator"
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/dist"

if ! command -v snapcraft >/dev/null 2>&1; then
  echo "snapcraft is required to build the Snap package." >&2
  echo "Install it first, then rerun this script." >&2
  exit 1
fi

mkdir -p "${DIST_DIR}"

before_list="$(mktemp)"
trap 'rm -f "${before_list}"' EXIT
find "${PROJECT_ROOT}" -maxdepth 1 -type f -name "${PROJECT_SLUG}_*.snap" -printf '%f\n' | sort > "${before_list}"

(
  cd "${PROJECT_ROOT}"
  snapcraft pack --destructive-mode --output "${PROJECT_ROOT}" "$@"
)

new_snap="$(comm -13 "${before_list}" <(
  find "${PROJECT_ROOT}" -maxdepth 1 -type f -name "${PROJECT_SLUG}_*.snap" -printf '%f\n' | sort
) | tail -n 1)"

if [ -z "${new_snap}" ]; then
  new_snap="$(find "${PROJECT_ROOT}" -maxdepth 1 -type f -name "${PROJECT_SLUG}_*.snap" -printf '%T@ %f\n' | sort -nr | awk 'NR == 1 { print $2 }')"
fi

if [ -z "${new_snap}" ]; then
  echo "snapcraft completed without producing a ${PROJECT_SLUG}_*.snap artifact." >&2
  exit 1
fi

mv -f "${PROJECT_ROOT}/${new_snap}" "${DIST_DIR}/${new_snap}"

echo "Created ${DIST_DIR}/${new_snap}"