#!/usr/bin/env python3
"""Constants and configuration for RClone Backup Manager.

This module centralizes all application constants, version information,
platform detection, and path configurations following Google Python style guide.
"""

import logging
import platform
import sys
from pathlib import Path

# Application metadata
VERSION = "2.0.0"
APP_NAME = "RClone Backup Manager"
GITHUB_REPO = "https://github.com/Nityam2007/rclone-backup-manager"
AUTHOR = "Nityam"

# GUI imports with ttkbootstrap for modern UI
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from tkinter import messagebox, scrolledtext, filedialog
    HAS_TTK_BOOTSTRAP = True
    HAS_TK = True
except ImportError:
    # Fallback to standard tkinter
    HAS_TTK_BOOTSTRAP = False
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext, filedialog
        HAS_TK = True
    except ImportError:
        HAS_TK = False
        print("ERROR: tkinter not available. Please install python3-tk")
        sys.exit(1)

# System tray imports availability check
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

# Modern UI Theme Configuration
DEFAULT_THEME = "cosmo"  # Modern light theme (flatly, cosmo, litera, minty, pulse)
DARK_THEME = "darkly"     # Modern dark theme (darkly, cyborg, superhero, solar)

# Modern Color Palette (Bootstrap-inspired)
COLORS = {
    'primary': '#0d6efd',    # Blue
    'success': '#198754',    # Green
    'warning': '#ffc107',    # Orange
    'danger': '#dc3545',     # Red
    'info': '#0dcaf0',       # Cyan
    'light': '#f8f9fa',      # Light gray
    'dark': '#212529',       # Dark gray
}


# Path configuration
# Handle both regular Python and PyInstaller executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable - use executable directory
    HERE = Path(sys.executable).parent
else:
    # Running as Python script
    HERE = Path(__file__).resolve().parent

CFG_FILE = HERE / 'folders.json'
LOG_FILE = HERE / 'backup_gui.log'
FIRST_RUN_FLAG = HERE / '.first_run_done'

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
