<!--
Version: 1.7.9
Date: 2026-08-12
Author: Serhii Dralo <dralo@ditis.group>
Changelog: Document seamless activity animation and landscape PDF reports in v1.7.9.
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
shasum -a 256 -c NetCheck-1.7.9-macos-x86_64.zip.sha256
ditto -x -k NetCheck-1.7.9-macos-x86_64.zip .
mv NetCheck.app /Applications/
```

Release builds are ad-hoc signed until an Apple Developer ID certificate is configured.
On first launch, Control-click NetCheck in Finder, choose **Open**, and confirm the macOS
security prompt. See [the release guide](docs/RELEASE.md) for signing details.

## Version 1.7.9 highlights

- PDF reports use A4 landscape orientation and compact seven-millimetre margins
- Wide discovery tables use smaller typography and predictable wrapping so every column fits
- The selected linear Aurora gradient moves in reverse at a constant speed with seamless repetition
- Matching start and end colors eliminate visible jumps; no white highlight or transparent edge is used

- Violet, muted magenta, and ruby accents enrich the animated activity spectrum
- Brand cyan and blue remain dominant, with adjacent transitions keeping every color harmonious
- The NetCheck wordmark matches the visual height of the adjacent author block

- The divider animates with the canonical DITIS cyan and navy colors during long-running operations
- Concurrent operations keep the activity animation running until every task completes

- Disabled actions remain dark blue with readable pale-blue text and icons
- Every action button uses the dark-navy brand surface by default and cyan on hover
- Primary navigation uses cyan for both hover and the active page
- Secondary navigation reverses the palette: cyan by default and navy for hover/active
- Combo boxes include a navy arrow control, cyan hover, white arrow, and styled popup list
- Button text and action icons remain white, with distinct pressed and disabled states

- Navigation uses 15 pixels below the cyan divider, 18 between tab rows, and 15 below
- Integer and decimal controls use 24-pixel navy steppers with white arrow icons

- Native dark-grey tab-row bases are removed from primary and secondary navigation
- Text, combo, integer, and decimal inputs keep identical frames before and during focus

- Ping and Route Monitor numeric controls align with their full-width target fields
- Wake-on-LAN controls start at the top of the panel instead of floating vertically
- Scan, copy, export, and Wake-on-LAN actions include compact accessible icons

- Secondary Tools and Settings navigation is approximately eight percent more compact

- Every compact form uses explicit 42-pixel labels aligned to the vertical center
- VLAN, Ports, Tools, Settings, and Profiles keep identical row alignment on macOS

- Primary and nested navigation menus are centered as complete fixed-width groups
- Centering remains stable across English, German, Russian, and Ukrainian labels

- Compact forms are centered horizontally and vertically in available content areas
- Form labels align with the vertical center of their input controls

- A single click copies the exact value of any populated result cell
- Brief localized copy confirmation appears beside the pointer

- Concurrent Ping of up to 16 hosts with configurable payload sizes up to 65,507 bytes
- Four-request finite Ping mode and cancellable continuous 100-request statistics batches
- Integrated MTR-style route monitor with per-hop loss and latency statistics
- Live Last, Average, Best, and Worst route-hop measurements
- Copy support for every result table through Command-C and context menus
- Network discovery report export to TXT, PDF, and vector SVG
- Vertically centered, consistently sized input controls
- Equal-width primary navigation without the unused grey tab-bar background

- One macOS administrator authorization for an entire VLAN list or range
- English, German, Russian, and Ukrainian interface languages
- Live per-VLAN progress with stabilized sequential DHCP acquisition
- Fast passive discovery of VLAN tags observed on a selected trunk interface
- Automatically refreshed interface selection for hot-plugged USB Ethernet adapters
- Restored DITIS branding and clearly styled primary actions
- Correct diagnostics that ignore unused disconnected and virtual bridge interfaces
- DITIS Group branding, transparent application icon, and author information
- Stable navy/cyan navigation, compact actions, and full-row table highlighting
- Automatic discovery subnet selection from the active Ethernet adapter
- Numeric IP sorting with reverse-DNS, mDNS cache, and NetBIOS name discovery
- NetBIOS information in discovery results and wider port scanner inputs
- Bootstrap-inspired navigation with consistent borders, spacing, and typography
- Taller padded inputs and square, single-grid tables for improved readability
- Live terminal-style output for Ping and Traceroute
- Bounded Traceroute probes that complete predictably on filtered networks
- A single macOS authorization captures LLDP and CDP together

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
