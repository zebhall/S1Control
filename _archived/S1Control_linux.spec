# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['S1Control.py'],
    pathex=[],
    binaries=[],
    datas=[('/home/zeb/.local/lib/python3.12/site-packages/customtkinter', 'customtkinter/'),("energies.csv","."),("pss_lb.png","."),("pss-logo2-med.png","."),("icons","icons")],
    hiddenimports=['plyer.platforms.linux.notification','PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='S1Control',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
