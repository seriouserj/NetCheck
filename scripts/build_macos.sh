#!/usr/bin/env bash
# Version: 1.0.0
# Date: 2026-08-07
# Author: NetCheck Contributors
# Changelog: Resolve configured Python commands through PATH for CI builds.

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_candidate="${PYTHON_BINARY:-${project_root}/.venv/bin/python}"
if ! python_binary="$(command -v "${python_candidate}")"; then
    echo "Python environment not found: ${python_candidate}" >&2
    exit 1
fi
version="$(cd "${project_root}" && "${python_binary}" -c 'from core.metadata import APP_VERSION; print(APP_VERSION)')"
architecture="$(uname -m)"
output_directory="${project_root}/dist"
output_app_path="${output_directory}/NetCheck.app"
archive_path="${project_root}/dist/NetCheck-${version}-macos-${architecture}.zip"
checksum_path="${archive_path}.sha256"
signing_identity="${NETCHECK_CODESIGN_IDENTITY:--}"
export PYINSTALLER_CONFIG_DIR="${project_root}/build/pyinstaller-cache"
staging_directory="$(mktemp -d /private/tmp/netcheck-build.XXXXXX)"
app_path="${staging_directory}/NetCheck.app"
staging_archive="${staging_directory}/$(basename "${archive_path}")"

cleanup() {
    rm -rf "${staging_directory}"
}
trap cleanup EXIT

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "NetCheck.app must be built on macOS." >&2
    exit 1
fi

"${python_binary}" -c 'import sys; assert sys.version_info[:2] == (3, 13), sys.version'
cd "${project_root}"
"${python_binary}" -m PyInstaller \
    --noconfirm \
    --clean \
    --distpath "${staging_directory}" \
    "${project_root}/NetCheck.spec"

# Cloud-backed folders may add Finder metadata that macOS refuses to sign.
xattr -cr "${app_path}"

if [[ "${signing_identity}" == "-" ]]; then
    codesign --force --deep --sign - "${app_path}"
else
    codesign --force --deep --options runtime --timestamp --sign "${signing_identity}" "${app_path}"
fi

codesign --verify --deep --strict --verbose=2 "${app_path}"
QT_QPA_PLATFORM=offscreen "${app_path}/Contents/MacOS/NetCheck" --smoke-test

mkdir -p "${output_directory}"
rm -rf "${output_app_path}"
ditto --noextattr --norsrc "${app_path}" "${output_app_path}"
rm -f "${archive_path}" "${checksum_path}"
ditto -c -k --sequesterRsrc --keepParent "${app_path}" "${staging_archive}"
cp "${staging_archive}" "${archive_path}"
shasum -a 256 "${archive_path}" >"${checksum_path}"

echo "Built ${output_app_path}"
echo "Archive ${archive_path}"
echo "Checksum ${checksum_path}"
