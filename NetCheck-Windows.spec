# -*- mode: python ; coding: utf-8 -*-
# Version: 1.8.1
# Date: 2026-08-12
# Author: Serhii Dralo <dralo@ditis.group>
# Changelog: Package the native NetCheck Windows x86-64 application.

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
    icon=str(project_root / "build" / "netcheck.ico"),
    version=str(project_root / "build" / "windows-version-info.txt"),
)

collection = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    name="NetCheck",
)
