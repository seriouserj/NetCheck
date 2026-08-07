<!--
Version: 1.0.1
Date: 2026-08-07
Author: NetCheck Contributors
Changelog: Add packaged macOS installation and release links.
-->

# NetCheck

NetCheck is a native macOS network diagnostic tool for system administrators, network
engineers, and IT support teams. It uses Python 3.13 and PySide6—no browser runtime or
Electron layer.

## Install the macOS application

Download the Intel macOS ZIP and its SHA-256 file from
[GitHub Releases](https://github.com/seriouserj/NetCheck/releases). Verify the download,
extract `NetCheck.app`, and move it to `Applications`:

```shell
shasum -a 256 -c NetCheck-1.0.0-macos-x86_64.zip.sha256
ditto -x -k NetCheck-1.0.0-macos-x86_64.zip .
mv NetCheck.app /Applications/
```

Release builds are ad-hoc signed until an Apple Developer ID certificate is configured.
On first launch, Control-click NetCheck in Finder, choose **Open**, and confirm the macOS
security prompt. See [the release guide](docs/RELEASE.md) for signing details.

## Quick start

```shell
python3.13 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

See [the full documentation](docs/README.md) for features, permissions, verification,
build instructions, and operational safety notes.
