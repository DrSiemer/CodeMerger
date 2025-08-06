# -*- mode: python ; coding: utf-8 -*-

data_files = [
    ('assets', 'assets'),
    ('default_filetypes.json', '.')
]

icon_path = 'assets/icon.ico'

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'PIL.ImageTk'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CodeMerger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path
)