#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_ARCHIVE_DIR="${REPO_ROOT}/artifacts/sources/archive"
DEFAULT_OUTPUT_ROOT="${REPO_ROOT}/artifacts/extracted/archive"
EXTRACTOR="${SCRIPT_DIR}/extract_reflexive_smart_installer.py"

usage() {
  cat <<'EOF'
Usage: extract_all_reflexive_smart_installers.sh [--force] [archive_dir] [output_root]

Extracts every `Reflexive Arcade *.exe` installer in the archive directory into:
  <output_root>/<installer stem>/

Defaults:
  archive_dir  = artifacts/sources/archive
  output_root  = artifacts/extracted/archive

Options:
  --force      Remove each existing output directory before extracting
EOF
}

force=0

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--force" ]]; then
  force=1
  shift
fi

if [[ $# -gt 2 ]]; then
  usage >&2
  exit 1
fi

archive_dir="${1:-${DEFAULT_ARCHIVE_DIR}}"
output_root="${2:-${DEFAULT_OUTPUT_ROOT}}"

if [[ ! -d "${archive_dir}" ]]; then
  printf 'archive directory does not exist: %s\n' "${archive_dir}" >&2
  exit 1
fi

if [[ ! -f "${EXTRACTOR}" ]]; then
  printf 'extractor script does not exist: %s\n' "${EXTRACTOR}" >&2
  exit 1
fi

mkdir -p "${output_root}"

shopt -s nullglob
installers=( "${archive_dir}"/Reflexive\ Arcade\ *.exe )
shopt -u nullglob

if [[ ${#installers[@]} -eq 0 ]]; then
  printf 'no installers found in %s\n' "${archive_dir}" >&2
  exit 1
fi

printf 'Archive directory: %s\n' "${archive_dir}"
printf 'Output root: %s\n' "${output_root}"
printf 'Installers: %d\n' "${#installers[@]}"

for installer in "${installers[@]}"; do
  stem="$(basename "${installer}" .exe)"
  destination="${output_root}/${stem}"

  printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "${stem}"

  cmd=( uv run "${EXTRACTOR}" "${installer}" "${destination}" )
  if [[ ${force} -eq 1 ]]; then
    cmd=( uv run "${EXTRACTOR}" --force "${installer}" "${destination}" )
  fi

  "${cmd[@]}"
done
