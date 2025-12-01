#!/usr/bin/env python3
"""Global constants and configuration."""

import logging
import platform
import sys
from pathlib import Path

# Metadata
VERSION = "2.1.1"
APP_NAME = "RClone Backup Manager"
GITHUB_REPO = "https://github.com/Nityam2007/rclone-backup-manager"
AUTHOR = "Nityam"

# GUI Framework
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from tkinter import messagebox, scrolledtext, filedialog
    HAS_TTK_BOOTSTRAP = True
    HAS_TK = True
except ImportError:
    HAS_TTK_BOOTSTRAP = False
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext, filedialog
        HAS_TK = True
    except ImportError:
        HAS_TK = False
        print("ERROR: tkinter not available. Please install python3-tk")
        sys.exit(1)

# System Tray Support
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# Platform
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

# Theme Settings
DEFAULT_THEME = "cosmo"
DARK_THEME = "darkly"

COLORS = {
    'primary': '#0d6efd',
    'success': '#198754',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#0dcaf0',
    'light': '#f8f9fa',
    'dark': '#212529',
}

# Paths
if getattr(sys, 'frozen', False):
    HERE = Path(sys.executable).parent
else:
    HERE = Path(__file__).resolve().parent

CFG_FILE = HERE / 'folders.json'
LOG_FILE = HERE / 'backup_gui.log'
FIRST_RUN_FLAG = HERE / '.first_run_done'

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
