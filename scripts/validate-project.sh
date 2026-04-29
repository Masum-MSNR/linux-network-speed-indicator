#!/usr/bin/env bash

set -euo pipefail

PYTHON_BIN="${PYTHON:-python3}"

"${PYTHON_BIN}" -m py_compile \
  src/network_speed_indicator.py \
  src/network_speed_indicator_core.py

"${PYTHON_BIN}" -m unittest discover -s tests -p 'test_*.py'

bash -n install.sh
bash -n uninstall.sh
bash -n scripts/build-deb.sh
bash -n scripts/build-flatpak.sh
bash -n scripts/build-snap.sh
bash -n scripts/sync-snap-store-listing.sh
bash -n scripts/build-release.sh

"${PYTHON_BIN}" -m json.tool config/default-config.json > /dev/null

if command -v appstreamcli >/dev/null 2>&1; then
  appstreamcli validate --no-net assets/metainfo/linux-network-speed-indicator.metainfo.xml
fi