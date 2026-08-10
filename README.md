<!--
Version: 1.4.0
Date: 2026-08-10
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Document the tubbeTEC-branded header in v1.4.0.
-->

# NetCheck

NetCheck is a native macOS network diagnostic tool for system administrators, network
engineers, and IT support teams. It uses Python 3.13 and PySide6—no browser runtime or
Electron layer.

## Install the macOS application

Download the latest Intel macOS ZIP and its SHA-256 file from
[GitHub Releases](https://github.com/seriouserj/NetCheck/releases). Verify the download,
extract `NetCheck.app`, and move it to `Applications`:

```shell
shasum -a 256 -c NetCheck-1.4.0-macos-x86_64.zip.sha256
ditto -x -k NetCheck-1.4.0-macos-x86_64.zip .
mv NetCheck.app /Applications/
```

Release builds are ad-hoc signed until an Apple Developer ID certificate is configured.
On first launch, Control-click NetCheck in Finder, choose **Open**, and confirm the macOS
security prompt. See [the release guide](docs/RELEASE.md) for signing details.

## Version 1.4 highlights

- One macOS administrator authorization for an entire VLAN list or range
- English, German, Russian, and Ukrainian interface languages
- Live per-VLAN progress with stabilized sequential DHCP acquisition
- Fast passive discovery of VLAN tags observed on a selected trunk interface
- Automatically refreshed interface selection for hot-plugged USB Ethernet adapters
- Persistent DITIS branding and clearly styled primary actions
- Correct diagnostics that ignore unused disconnected and virtual bridge interfaces
- DITIS Group branding, transparent application icon, and author information
- Stable navy/cyan navigation, compact actions, and full-row table highlighting
- Automatic discovery subnet selection from the active Ethernet adapter
- Numeric IP sorting with reverse-DNS, mDNS cache, and NetBIOS name discovery
- NetBIOS information in discovery results and wider port scanner inputs
- Compact segmented navigation in Tools and Settings
- Centered, consistently sized DNS and Wake-on-LAN actions
- tubbeTEC logo and concise “NetCheck Tool by Serhii Dralo” header identity

NetCheck is authored by [Serhii Dralo](mailto:dralo@ditis.group).

## Quick start

```shell
python3.13 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

See [the full documentation](docs/README.md) for features, permissions, verification,
build instructions, and operational safety notes.
