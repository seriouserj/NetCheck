<!--
Version: 1.1.0
Date: 2026-08-07
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Document localization, single-prompt VLAN tests, and product branding.
-->

# NetCheck

NetCheck is a native macOS network diagnostic application for system administrators,
network engineers, and IT support professionals.

## Requirements

- macOS
- Python 3.13
- A USB Ethernet adapter for wired diagnostics

## Run locally

```shell
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

The application uses native Qt 6 widgets through PySide6 and follows the active macOS
light or dark appearance.

## Packaged application

Tagged releases provide an Intel macOS ZIP that contains `NetCheck.app` and does not
require a separate Python installation. Verify the accompanying SHA-256 file before
opening it. Until a Developer ID certificate is configured, builds use an ad-hoc
signature and require the standard first-launch confirmation in Finder.

For reproducible builds, artifact naming, signing, and release automation, see the
[release guide](RELEASE.md).

## Features

- Ethernet dashboard with link, speed, duplex, addressing, routes, DNS, and connectivity
- Temporary VLAN testing for IDs and ranges from 1 through 4094
- Concurrent IPv4 discovery with hostname, MAC vendor, and latency
- Concurrent TCP connect scanner with Open, Closed, and Filtered states
- Ping, traceroute, DNS lookup, and Wake-on-LAN tools
- Persistent timeouts, preferred DNS, default interface, and theme settings
- Reusable location profiles with VLAN, DNS, and subnet defaults
- Smart Diagnostics with probable causes and recommended corrective actions
- Passive LLDP and CDP neighbor discovery
- Read-only SNMP v2c GET and WALK operations
- Runtime English, German, Russian, and Ukrainian localization

An entire VLAN list or range runs inside one privileged worker and therefore requests
macOS administrator authorization once per test batch. Temporary interfaces are still
removed after each VLAN, including failure paths.

## Author

NetCheck is authored by Serhii Dralo, [dralo@ditis.group](mailto:dralo@ditis.group),
with official branding from [DITIS Group](https://ditis.group).

## macOS permissions

Temporary VLAN creation and passive LLDP/CDP capture use the standard macOS
administrator authorization dialog. NetCheck never stores administrator credentials or
SNMP community strings. Temporary VLAN interfaces are removed even when a test fails.

Only scan networks and devices you are authorized to test.

## Verify

```shell
python3 -m ruff check main.py core ui profiles scripts tests
python3 -m pytest -q
QT_QPA_PLATFORM=offscreen python3 scripts/smoke_test.py
```

The stable release is verified with Python 3.13 on macOS.
