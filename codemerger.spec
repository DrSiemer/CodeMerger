# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# --- Tcl/Tk Path Discovery Helper ---
def get_tcl_tk_paths():
    """Locates the Tcl and Tk library directories in the current Python environment."""
    prefixes = [sys.prefix, getattr(sys, 'base_prefix', sys.prefix)]
    tcl_tk_datas = []

    for prefix in prefixes:
        tcl_root = os.path.join(prefix, 'tcl')
        if os.path.exists(tcl_root):
            for entry in os.listdir(tcl_root):
                full_path = os.path.join(tcl_root, entry)
                if os.path.isdir(full_path):
                    if entry.startswith('tcl8'):
                        tcl_tk_datas.append((full_path, 'tcl'))
                    elif entry.startswith('tk8'):
                        tcl_tk_datas.append((full_path, 'tk'))

            if tcl_tk_datas:
                return tcl_tk_datas
    return []

# --- Main Application Analysis ---
app_data_files = [
    ('assets', 'assets'),
    ('default_filetypes.json', '.'),
    ('version.txt', '.')
]

# Explicitly add Tcl/Tk data to the bundle
app_data_files.extend(get_tcl_tk_paths())

app_icon_path = 'assets/icon.ico'
install_icon_path = 'assets/install.ico'

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=app_data_files,
    hiddenimports=[
        'PIL.ImageTk',
        'tiktoken_ext.openai_public',
        'detect_secrets.plugins',
        'rich',
        'markdown2'
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
    datas=[(install_icon_path, 'assets')],
    hiddenimports=[],
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
    icon=install_icon_path
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