# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['S1Control.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/Zeb/AppData/Roaming/Python/Python311/site-packages/customtkinter', 'customtkinter/'),("energies.csv","."),("pss_lb.ico","."),("pss-logo2-med.png","."),("icons","icons")],
    hiddenimports=[],
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
    a.binaries,
    a.zipfiles,
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
    icon=['pss_lb.ico'],
)
