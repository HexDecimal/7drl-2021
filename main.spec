# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[("Alloy_curses_12x12.png", ".")],
    hiddenimports=[
        "scipy.spatial.transform._rotation_groups",  # Fix 'PyInstaller < 4.2'
    ],
    hookspath=[],
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
    name="start_game",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name="RayWizard")
