#!/usr/bin/env bash

set -euo pipefail

SNAP_NAME="linux-network-speed-indicator"
PRIMARY_CATEGORY="${SNAP_STORE_PRIMARY_CATEGORY:-utilities}"
PYTHON_BIN="${PYTHON:-python3}"
SCREENSHOT_FILES=(
  "${SNAP_STORE_SCREENSHOT_1:-assets/screenshots/overview.png}"
  "${SNAP_STORE_SCREENSHOT_2:-assets/screenshots/menu.png}"
)

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_file() {
  if [ ! -f "$1" ]; then
    echo "Missing required file: $1" >&2
    exit 1
  fi
}

json_get() {
  local filter="$1"

  printf '%s' "$CREDENTIALS_JSON" | jq -r "$filter"
}

api_call() {
  local output_file="$1"
  shift

  curl -sS -o "$output_file" -w '%{http_code}' \
    -H "Authorization: ${AUTHORIZATION_HEADER}" \
    -H 'Accept: application/json' \
    "$@"
}

require_command base64
require_command curl
require_command jq
require_command sha256sum
require_command "$PYTHON_BIN"

if [ -z "${SNAPCRAFT_STORE_CREDENTIALS:-}" ]; then
  echo 'SNAPCRAFT_STORE_CREDENTIALS is required.' >&2
  exit 1
fi

for screenshot_file in "${SCREENSHOT_FILES[@]}"; do
  require_file "$screenshot_file"
done

CREDENTIALS_JSON="$(printf '%s' "$SNAPCRAFT_STORE_CREDENTIALS" | base64 --decode)"
CREDENTIAL_TYPE="$(json_get '.t')"

if [ "$CREDENTIAL_TYPE" != 'u1-macaroon' ]; then
  echo "Unsupported Snap Store credential type: $CREDENTIAL_TYPE" >&2
  exit 1
fi

AUTHORIZATION_HEADER="$(CREDENTIALS_JSON="$CREDENTIALS_JSON" "$PYTHON_BIN" - <<'PY'
import json
import os
import sys

try:
    from pymacaroons import Macaroon
except ImportError as exc:
    raise SystemExit(
        'Missing Python dependency: pymacaroons. Install it before running listing sync.'
    ) from exc

credentials = json.loads(os.environ['CREDENTIALS_JSON'])
root_macaroon = credentials['v']['r']
discharge_macaroon = credentials['v']['d']
bound_discharge = Macaroon.deserialize(root_macaroon).prepare_for_request(
    Macaroon.deserialize(discharge_macaroon)
).serialize()
sys.stdout.write(f'Macaroon root={root_macaroon}, discharge={bound_discharge}')
PY
)"

SNAP_ID="$({
  curl -fsS \
    -H 'Snap-Device-Series: 16' \
    -H 'Accept: application/json' \
    "https://api.snapcraft.io/v2/snaps/info/${SNAP_NAME}?fields=title,snap-id,name,store-url"
} | jq -r '.["snap-id"] // .snap["snap-id"]')"

if [ -z "$SNAP_ID" ] || [ "$SNAP_ID" = 'null' ]; then
  echo "Failed to resolve snap-id for ${SNAP_NAME}." >&2
  exit 1
fi

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

METADATA_PAYLOAD="$(jq -nc --arg category "$PRIMARY_CATEGORY" '{categories: [$category]}')"
METADATA_STATUS="$(api_call "$TMP_DIR/metadata.json" \
  -X POST \
  -H 'Content-Type: application/json' \
  -d "$METADATA_PAYLOAD" \
  "https://dashboard.snapcraft.io/dev/api/snaps/${SNAP_ID}/metadata")"

case "$METADATA_STATUS" in
  2*)
    echo "Updated Snap Store category to ${PRIMARY_CATEGORY}."
    ;;
  *)
    echo "Failed to update Snap Store category (HTTP ${METADATA_STATUS})." >&2
    cat "$TMP_DIR/metadata.json" >&2
    exit 1
    ;;
esac

SCREENSHOT_1_HASH="$(sha256sum "${SCREENSHOT_FILES[0]}" | cut -d' ' -f1)"
SCREENSHOT_2_HASH="$(sha256sum "${SCREENSHOT_FILES[1]}" | cut -d' ' -f1)"

SCREENSHOT_1_MIME_TYPE="$(file --brief --mime-type "${SCREENSHOT_FILES[0]}")"
SCREENSHOT_2_MIME_TYPE="$(file --brief --mime-type "${SCREENSHOT_FILES[1]}")"

CURRENT_BINARY_STATUS="$(api_call "$TMP_DIR/current-binary-metadata.json" \
  -X GET \
  "https://dashboard.snapcraft.io/dev/api/snaps/${SNAP_ID}/binary-metadata")"

case "$CURRENT_BINARY_STATUS" in
  2*)
    ;;
  *)
    echo "Failed to fetch current Snap Store binary metadata (HTTP ${CURRENT_BINARY_STATUS})." >&2
    cat "$TMP_DIR/current-binary-metadata.json" >&2
    exit 1
    ;;
esac

PRESERVED_BINARY_INFO="$(jq -c '[.[] | select(.type != "screenshot")]' "$TMP_DIR/current-binary-metadata.json")"

BINARY_INFO="$(jq -nc \
  --argjson preserved_binary_info "$PRESERVED_BINARY_INFO" \
  --arg screenshot_1_hash "$SCREENSHOT_1_HASH" \
  --arg screenshot_2_hash "$SCREENSHOT_2_HASH" \
  --arg screenshot_1_filename "$(basename "${SCREENSHOT_FILES[0]}")" \
  --arg screenshot_2_filename "$(basename "${SCREENSHOT_FILES[1]}")" \
  '$preserved_binary_info + [
      {key: "screenshot_1", type: "screenshot", filename: $screenshot_1_filename, hash: $screenshot_1_hash},
      {key: "screenshot_2", type: "screenshot", filename: $screenshot_2_filename, hash: $screenshot_2_hash}
    ]')"

BINARY_STATUS="$(api_call "$TMP_DIR/binary-metadata.json" \
  -X PUT \
  -F "info=${BINARY_INFO}" \
  -F "screenshot_1=@${SCREENSHOT_FILES[0]};type=${SCREENSHOT_1_MIME_TYPE}" \
  -F "screenshot_2=@${SCREENSHOT_FILES[1]};type=${SCREENSHOT_2_MIME_TYPE}" \
  "https://dashboard.snapcraft.io/dev/api/snaps/${SNAP_ID}/binary-metadata")"

case "$BINARY_STATUS" in
  2*)
    echo 'Updated Snap Store screenshots.'
    ;;
  *)
    echo "Failed to update Snap Store binary metadata (HTTP ${BINARY_STATUS})." >&2
    cat "$TMP_DIR/binary-metadata.json" >&2
    exit 1
    ;;
esac