<!--
Version: 1.3.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Update reproducible build and artifact examples for v1.3.0.
-->

# macOS release guide

NetCheck uses PyInstaller to create a native Intel macOS application bundle. The bundle
contains Python 3.13 and all runtime dependencies, so end users do not install Python or
PySide6 separately.

## Build locally

Create a Python 3.13 environment, install both dependency sets, and run the build script:

```shell
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
scripts/build_macos.sh
```

The build validates the Python version, creates `dist/NetCheck.app`, signs and verifies
the bundle, runs a headless UI smoke test, and creates these release files:

- `dist/NetCheck-1.3.0-macos-x86_64.zip`
- `dist/NetCheck-1.3.0-macos-x86_64.zip.sha256`

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

The `Release` GitHub Actions workflow runs on version tags. It installs Python 3.13,
validates the source, builds the application, uploads the ZIP and checksum as workflow
artifacts, and attaches them to the matching GitHub Release.

Create and push an annotated version tag only after the `CI` workflow passes on `main`:

```shell
git tag -a v1.3.0 -m "NetCheck v1.3.0"
git push origin main
git push origin v1.3.0
```

Before publishing, verify that the release ZIP matches its checksum and that the app
opens on a supported Intel Mac.
