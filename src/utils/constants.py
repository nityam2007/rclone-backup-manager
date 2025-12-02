# Global Constants and Configuration | Python
"""Global constants, logging setup, and framework imports."""

import logging
import platform
import sys
from pathlib import Path

# Metadata
VERSION = "2.2.0"
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

# Platform Detection
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'
IS_MAC = platform.system() == 'Darwin'

# Theme Settings
DEFAULT_THEME = "cosmo"
DARK_THEME = "darkly"

COLORS = {
    'primary': '#0d6efd',
    'secondary': '#6c757d',
    'success': '#198754',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#0dcaf0',
    'light': '#f8f9fa',
    'dark': '#212529',
    'muted': '#6c757d',
    'white': '#ffffff',
    'bg_light': '#f5f7fa',
    'border': '#dee2e6',
    'text_primary': '#212529',
    'text_secondary': '#6c757d',
}

# Paths - Root level for main files, data/ for state
if getattr(sys, 'frozen', False):
    HERE = Path(sys.executable).parent
else:
    HERE = Path(__file__).resolve().parent.parent.parent

# Main config stays in root
CFG_FILE = HERE / 'folders.json'
LOG_FILE = HERE / 'backup_gui.log'
FIRST_RUN_FLAG = HERE / '.first_run_done'

# State file goes in data/
DATA_DIR = HERE / 'data'
STATE_FILE = DATA_DIR / 'state.json'

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
