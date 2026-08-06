<!--
Version: 0.1.0
Date: 2026-08-06
Author: NetCheck Contributors
Changelog: Initial developer documentation.
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
