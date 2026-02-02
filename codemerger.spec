# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# --- Tcl/Tk Correct Folder Mapping ---
def get_tcl_tk_datas():
    """
    Finds Tcl/Tk and maps the CONTENTS of the versioned folders
    directly into _tcl_data and _tk_data to satisfy PyInstaller hooks.
    """
    prefixes = [sys.prefix, getattr(sys, 'base_prefix', sys.prefix)]
    tcl_tk_datas = []

    for prefix in prefixes:
        tcl_root = os.path.join(prefix, 'tcl')
        if os.path.exists(tcl_root):
            tcl_dir = ""
            tk_dir = ""
            for entry in os.listdir(tcl_root):
                if entry.startswith('tcl8.'): tcl_dir = entry
                if entry.startswith('tk8.'): tk_dir = entry

            if tcl_dir and tk_dir:
                tcl_path = os.path.join(tcl_root, tcl_dir)
                tk_path = os.path.join(tcl_root, tk_dir)

                # --- FIX: Map the CONTENTS directly to the hook-expected folders ---
                # By mapping to '_tcl_data' instead of '_tcl_data/tcl8.6',
                # we ensure init.tcl is found at _internal/_tcl_data/init.tcl
                tcl_tk_datas.append((tcl_path, '_tcl_data'))
                tcl_tk_datas.append((tk_path, '_tk_data'))

                os.environ['TCL_LIBRARY'] = tcl_path
                os.environ['TK_LIBRARY'] = tk_path
                return tcl_tk_datas
    return []

# Load the Tcl/Tk data once
tcl_tk_data_bundle = get_tcl_tk_datas()

# --- Main Application Analysis ---
app_data_files = [
    ('assets', 'assets'),
    ('default_filetypes.json', '.'),
    ('version.txt', '.')
]
app_data_files.extend(tcl_tk_data_bundle)

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
# Added Tcl/Tk data here as well to prevent updater crashes
updater_datas = [(install_icon_path, 'assets')]
updater_datas.extend(tcl_tk_data_bundle)

updater_a = Analysis(
    ['updater_gui.py'],
    pathex=[],
    binaries=[],
    datas=updater_datas,
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