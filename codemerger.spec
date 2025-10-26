# -*- mode: python ; coding: utf-8 -*-

# --- Main Application Analysis ---
app_data_files = [
    ('assets', 'assets'),
    ('default_filetypes.json', '.'),
    ('version.txt', '.')
]
app_icon_path = 'assets/icon.ico'

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=app_data_files,
    hiddenimports=[
        'PIL.ImageTk',
        'tiktoken_ext.openai_public',
        'detect_secrets.plugins',
        'psutil'
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
    [],
    name='CodeMerger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=app_icon_path
)

# --- Updater GUI Launcher Analysis ---
updater_a = Analysis(
    ['updater_gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
updater_pyz = PYZ(updater_a.pure)

updater_exe = EXE(
    updater_pyz,
    updater_a.scripts,
    [],
    name='updater_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon=app_icon_path
)

# --- Collection ---
coll = COLLECT(
    exe,
    updater_exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CodeMerger'
)