# -*- mode: python ; coding: utf-8 -*-
# Phase 5.1: PyInstaller spec for macOS .app bundle (no console window).

import sys
from pathlib import Path

block_cipher = None

SRC = Path(".")

a = Analysis(
    [str(SRC / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        (str(SRC / "sandbox" / "Dockerfile"), "sandbox"),
    ],
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        "pynput.keyboard._darwin",
        "pynput.mouse._darwin",
        "docker",
        "anthropic",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Charmstone",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,       # --noconsole: no terminal window on launch
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Charmstone",
)

app = BUNDLE(
    coll,
    name="Charmstone.app",
    icon=None,           # replace with a .icns path if desired
    bundle_identifier="com.charmstone.app",
    info_plist={
        "NSHighResolutionCapable": True,
        "LSUIElement": True,          # hide from Dock (runs as agent)
        "NSAppleEventsUsageDescription":
            "Charmstone needs Automation access to read the selected folder in Finder.",
        "NSAccessibilityUsageDescription":
            "Charmstone needs Accessibility access to register global keyboard shortcuts.",
    },
)
