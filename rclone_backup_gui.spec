# -*- mode: python ; coding: utf-8 -*-
# RClone Backup Manager - PyInstaller Spec | Python
# Fully self-contained single executable - no Python needed on target

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect ALL components from each library
datas = []
binaries = []
hiddenimports = []

# ttkbootstrap - theming library
for pkg in ['ttkbootstrap']:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# PIL/Pillow - image handling
for pkg in ['PIL']:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# pystray - system tray
for pkg in ['pystray']:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Additional hidden imports
hiddenimports += [
    # ttkbootstrap essentials
    'ttkbootstrap',
    'ttkbootstrap.style',
    'ttkbootstrap.themes',
    'ttkbootstrap.themes.standard',
    'ttkbootstrap.tooltip',
    'ttkbootstrap.constants',
    
    # PIL essentials
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageTk',
    
    # pystray backends
    'pystray._xorg',
    'pystray._gtk',
    'pystray._appindicator',
    
    # tkinter (should be bundled with python)
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.filedialog',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'pytest', 'IPython', 'setuptools', 'pip',
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
