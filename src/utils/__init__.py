# Utils Package | Python
"""Utility modules and constants."""

from .constants import (
    VERSION, APP_NAME, GITHUB_REPO, AUTHOR,
    HAS_TK, HAS_TTK_BOOTSTRAP, HAS_TRAY,
    IS_WINDOWS, IS_LINUX,
    DEFAULT_THEME, DARK_THEME, COLORS,
    HERE, CFG_FILE, LOG_FILE, STATE_FILE, FIRST_RUN_FLAG,
    logger, ttk, messagebox, scrolledtext, filedialog
)
from .tray_manager import TrayManager

__all__ = [
    'VERSION', 'APP_NAME', 'GITHUB_REPO', 'AUTHOR',
    'HAS_TK', 'HAS_TTK_BOOTSTRAP', 'HAS_TRAY',
    'IS_WINDOWS', 'IS_LINUX',
    'DEFAULT_THEME', 'DARK_THEME', 'COLORS',
    'HERE', 'CFG_FILE', 'LOG_FILE', 'STATE_FILE', 'FIRST_RUN_FLAG',
    'logger', 'ttk', 'messagebox', 'scrolledtext', 'filedialog',
    'TrayManager'
]
