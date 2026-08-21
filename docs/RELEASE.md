<!--
Version: 1.9.3
Date: 2026-08-21
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Document release 1.9.3 artifact names.
-->

# macOS and Windows release guide

NetCheck uses PyInstaller to create a native Intel macOS application bundle. The bundle
contains Python 3.13 and all runtime dependencies, so end users do not install Python or
PySide6 separately.

## Build macOS locally

Create a Python 3.13 environment, install both dependency sets, and run the build script:

```shell
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
scripts/build_macos.sh
```

The build validates the Python version, creates `dist/NetCheck.app`, signs and verifies
the bundle, runs a headless UI smoke test, and creates these release files:

- `dist/NetCheck-1.9.3-macos-x86_64.zip`
- `dist/NetCheck-1.9.3-macos-x86_64.zip.sha256`

## Build Windows locally

On a Windows x86-64 system with Python 3.13, install the dependency sets and
run the PowerShell build script:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
.\scripts\build_windows.ps1
```

The script creates and verifies:

- `dist/NetCheck-1.9.3-windows-x86_64.zip`
- `dist/NetCheck-1.9.3-windows-x86_64.zip.sha256`

Build and signing take place in a temporary local directory. This prevents iCloud and
other File Provider metadata from invalidating the macOS code signature.

## Code signing

The default build uses an ad-hoc signature. It verifies bundle integrity but does not
identify an Apple developer and cannot be notarized. Users must approve the first launch
through Finder by Control-clicking the application and choosing **Open**.

To produce a Developer ID signed build, import the certificate into the login keychain
and provide its full identity:

```shell
NETCHECK_CODESIGN_IDENTITY="Developer ID Application: Example GmbH (TEAMID)" \
  scripts/build_macos.sh
```

Apple notarization requires an active Apple Developer Program account and credentials.
Those credentials must remain outside the repository. Notarization and stapling should
be performed after the Developer ID build and before public distribution.

## Automated release

The `Release` GitHub Actions workflow runs on version tags. Separate native runners
build macOS Intel and Windows x86-64 packages. A publication job downloads both verified
artifact sets and attaches them to one matching GitHub Release.

Create and push an annotated version tag only after the `CI` workflow passes on `main`:

```shell
git tag -a v1.9.3 -m "NetCheck v1.9.3"
git push origin main
git push origin v1.9.3
```

Before publishing, verify that the release ZIP matches its checksum and that the app
opens on a supported Intel Mac and Windows x86-64 system.
