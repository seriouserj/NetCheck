# -*- mode: python ; coding: utf-8 -*-
# Version: 1.9.1
# Date: 2026-08-13
# Author: Serhii Dralo <dralo@ditis.group>
# Changelog: Package restored macOS dashboard address reporting.

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files


project_root = Path(SPECPATH)
manuf_data = collect_data_files("manuf")
brand_data = [
    (str(project_root / "icons" / "ditis-logo.svg"), "icons"),
    (str(project_root / "icons" / "ditis-logo.png"), "icons"),
    (str(project_root / "icons" / "netcheck-1024.png"), "icons"),
    (str(project_root / "icons" / "step-up-white.svg"), "icons"),
    (str(project_root / "icons" / "step-down-white.svg"), "icons"),
]

analysis = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[*manuf_data, *brand_data],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=1,
)

python_archive = PYZ(analysis.pure)

executable = EXE(
    python_archive,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="NetCheck",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="NetCheck",
)

app = BUNDLE(
    collection,
    name="NetCheck.app",
    icon=str(project_root / "icons" / "netcheck-1024.png"),
    bundle_identifier="com.tubbetec.netcheck",
    version="1.9.1",
    info_plist={
        "CFBundleDisplayName": "NetCheck",
        "CFBundleShortVersionString": "1.9.1",
        "CFBundleVersion": "35",
        "CFBundleGetInfoString": "NetCheck 1.9.1 — Serhii Dralo <dralo@ditis.group>",
        "NSHumanReadableCopyright": "Copyright © 2026 Serhii Dralo. All rights reserved.",
        "LSMinimumSystemVersion": "13.0",
        "NSHighResolutionCapable": True,
        "NSLocalNetworkUsageDescription": "NetCheck scans local networks selected by the user for diagnostics.",
        "NSPrincipalClass": "NSApplication",
    },
)
