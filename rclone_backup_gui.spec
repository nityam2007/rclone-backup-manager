# -*- mode: python ; coding: utf-8 -*-
# RClone Backup Manager - PyInstaller Spec (Onefile) | Python
# Complete spec with all dependencies properly included

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect all ttkbootstrap components
ttkbootstrap_datas, ttkbootstrap_binaries, ttkbootstrap_hiddenimports = collect_all('ttkbootstrap')

# Collect PIL/Pillow
pil_datas, pil_binaries, pil_hiddenimports = collect_all('PIL')

# Collect pystray
pystray_hiddenimports = collect_submodules('pystray')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=ttkbootstrap_binaries + pil_binaries,
    datas=ttkbootstrap_datas + pil_datas,
    hiddenimports=[
        # ttkbootstrap (theming library)
        'ttkbootstrap',
        'ttkbootstrap.style',
        'ttkbootstrap.themes',
        'ttkbootstrap.themes.standard',
        'ttkbootstrap.themes.user',
        'ttkbootstrap.localization',
        'ttkbootstrap.localization.msgs',
        'ttkbootstrap.tooltip',
        'ttkbootstrap.constants',
        'ttkbootstrap.publisher',
        'ttkbootstrap.colorutils',
        'ttkbootstrap.utility',
        'ttkbootstrap.icons',
        'ttkbootstrap.dialogs',
        'ttkbootstrap.scrolled',
        'ttkbootstrap.tableview',
        'ttkbootstrap.window',
        'ttkbootstrap.widgets',
        
        # PIL/Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        
        # pystray (system tray)
        'pystray',
        'pystray._base',
        'pystray._xorg',
        'pystray._util',
        'pystray._util.gtk',
        'pystray._util.x11',
        
        # tkinter core
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        '_tkinter',
        
        # Standard library used by app
        'json',
        'logging',
        'subprocess',
        'threading',
        'platform',
        'pathlib',
        'datetime',
        'argparse',
        're',
        'shlex',
        'time',
        'typing',
        
    ] + ttkbootstrap_hiddenimports + pil_hiddenimports + pystray_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused heavy libs
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'unittest',
        'IPython',
        'notebook',
        'sphinx',
        'setuptools',
        'distutils',
        'wheel',
        'pip',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='rclone-backup-manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
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
