#!/usr/bin/env bash
set -euo pipefail

ITEM_ID="reflexivearcadegamescollection"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_DEST="${REPO_ROOT}/artifacts/archive/${ITEM_ID}"

usage() {
  cat <<'EOF'
Usage: download_reflexivearcadegamescollection.sh [destination]

Downloads the full Archive.org item `reflexivearcadegamescollection` with aria2.
If the destination is omitted, files are written to:
  artifacts/archive/reflexivearcadegamescollection

Environment overrides:
  ARIA2_MAX_CONCURRENT_DOWNLOADS   Default: 4
  ARIA2_MAX_CONNECTIONS_PER_SERVER Default: 4
  ARIA2_SPLIT                      Default: 4
  ARIA2_MIN_SPLIT_SIZE             Default: 16M
  ARIA2_SUMMARY_INTERVAL           Default: 30
EOF
}

require_cmd() {
  local cmd="$1"

  if ! command -v "${cmd}" >/dev/null 2>&1; then
    printf 'missing required command: %s\n' "${cmd}" >&2
    exit 1
  fi
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 1 ]]; then
  usage >&2
  exit 1
fi

require_cmd aria2c
require_cmd curl
require_cmd jq

dest_dir="${1:-${DEFAULT_DEST}}"
metadata_url="https://archive.org/metadata/${ITEM_ID}"
download_base="https://archive.org/download/${ITEM_ID}"
manifest_path="$(mktemp -t "${ITEM_ID}.aria2")"
trap 'rm -f "${manifest_path}"' EXIT

metadata_json="$(curl -fsSL "${metadata_url}")"
files_count="$(jq -r '.files_count' <<<"${metadata_json}")"
item_size="$(jq -r '.item_size' <<<"${metadata_json}")"

mkdir -p "${dest_dir}"

jq -r --arg download_base "${download_base}" --arg dir "${dest_dir}" '
  .files[]
  | select(.name | endswith(".torrent") | not)
  | "\($download_base)/\(.name | @uri)\n dir=\($dir)\n out=\(.name)\n"
' <<<"${metadata_json}" > "${manifest_path}"

printf 'Item: %s\n' "${ITEM_ID}"
printf 'Destination: %s\n' "${dest_dir}"
printf 'Files: %s\n' "${files_count}"
printf 'Total bytes: %s\n' "${item_size}"

exec aria2c \
  --continue=true \
  --allow-overwrite=false \
  --auto-file-renaming=false \
  --file-allocation=none \
  --follow-torrent=false \
  --follow-metalink=false \
  --remote-time=true \
  --summary-interval="${ARIA2_SUMMARY_INTERVAL:-30}" \
  --max-concurrent-downloads="${ARIA2_MAX_CONCURRENT_DOWNLOADS:-4}" \
  --max-connection-per-server="${ARIA2_MAX_CONNECTIONS_PER_SERVER:-4}" \
  --split="${ARIA2_SPLIT:-4}" \
  --min-split-size="${ARIA2_MIN_SPLIT_SIZE:-16M}" \
  --input-file="${manifest_path}"
