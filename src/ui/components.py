# UI Components | Python
"""Reusable UI components and helper widgets."""

import platform
import subprocess
import tkinter as tk
from typing import Dict, Tuple, Optional, Callable

from ..utils.constants import (
    APP_NAME, VERSION, AUTHOR, GITHUB_REPO,
    CFG_FILE, LOG_FILE, HAS_TRAY, HAS_TTK_BOOTSTRAP,
    COLORS, ttk, messagebox, scrolledtext
)
from .theme import ICONS, get_font, SPACING


def create_tooltip(widget, text: str):
    """Attach a tooltip to a widget."""
    if HAS_TTK_BOOTSTRAP:
        try:
            from ttkbootstrap.tooltip import ToolTip
            ToolTip(widget, text=text, delay=500)
        except Exception:
            pass


class ModernCard(ttk.Frame):
    """A modern card-style container widget."""
    
    def __init__(self, parent, title: str = "", padding: int = 15, **kwargs):
        super().__init__(parent, **kwargs)
        
        if HAS_TTK_BOOTSTRAP:
            self.configure(bootstyle="default")
        
        # Title bar if provided
        if title:
            title_frame = ttk.Frame(self)
            title_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(
                title_frame,
                text=title,
                font=get_font(11, 'bold')
            ).pack(side=tk.LEFT)
        
        # Content area
        self.content = ttk.Frame(self, padding=padding)
        self.content.pack(fill=tk.BOTH, expand=True)
    
    def get_content(self) -> ttk.Frame:
        """Get the content frame."""
        return self.content


class IconButton(ttk.Button):
    """A button with an icon prefix."""
    
    def __init__(self, parent, icon: str, text: str = "", **kwargs):
        display_text = f"{ICONS.get(icon, '')} {text}".strip()
        super().__init__(parent, text=display_text, **kwargs)


class StatusIndicator(ttk.Frame):
    """A status indicator with icon and label."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.icon_label = ttk.Label(self, text=ICONS['info'], font=('', 12))
        self.icon_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.text_label = ttk.Label(self, text="Ready")
        self.text_label.pack(side=tk.LEFT)
    
    def set_status(self, status: str, text: str):
        """Update the status display."""
        icon_map = {
            'success': (ICONS['success'], COLORS['success']),
            'error': (ICONS['error'], COLORS['danger']),
            'warning': (ICONS['warning'], COLORS['warning']),
            'running': (ICONS['loading'], COLORS['primary']),
            'idle': (ICONS['info'], COLORS['muted']),
        }
        
        icon, color = icon_map.get(status, (ICONS['info'], COLORS['text_primary']))
        self.icon_label.config(text=icon, foreground=color)
        self.text_label.config(text=text)


def create_menu_bar(root, callbacks: Dict) -> tk.Menu:
    """Create the application menu bar."""
    menubar = tk.Menu(root)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    
    file_menu.add_command(
        label=f"{ICONS['refresh']} Reload Config",
        command=callbacks.get('reload_config'),
        accelerator="F5"
    )
    file_menu.add_command(
        label=f"{ICONS['file']} View Config File",
        command=callbacks.get('view_config_file')
    )
    file_menu.add_separator()
    file_menu.add_command(
        label=f"{ICONS['close']} Exit",
        command=callbacks.get('on_close'),
        accelerator="Ctrl+Q"
    )
    
    # View menu
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    
    view_menu.add_command(
        label=f"{ICONS['settings']} Toggle Dark Mode",
        command=callbacks.get('toggle_dark_mode')
    )
    view_menu.add_checkbutton(
        label="Minimize to Tray",
        command=callbacks.get('toggle_tray')
    )
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    
    help_menu.add_command(
        label=f"{ICONS['file']} Documentation",
        command=callbacks.get('show_documentation')
    )
    help_menu.add_command(
        label=f"{ICONS['settings']} Keyboard Shortcuts",
        command=callbacks.get('show_shortcuts')
    )
    help_menu.add_separator()
    help_menu.add_command(
        label=f"{ICONS['info']} About",
        command=callbacks.get('show_about')
    )
    
    return menubar


def create_status_bar(parent, initial_text: str = "Ready") -> Tuple[ttk.Label, ttk.Label]:
    """Create a modern status bar."""
    status_frame = ttk.Frame(parent)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Left side - main status
    left_frame = ttk.Frame(status_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
    
    status_label = ttk.Label(
        left_frame,
        text=f"{ICONS['success']} {initial_text}",
        font=get_font(9)
    )
    status_label.pack(side=tk.LEFT)
    
    # Right side - backup count
    right_frame = ttk.Frame(status_frame)
    right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    
    backup_count_label = ttk.Label(
        right_frame,
        text=f"{ICONS['folder']} 0 backup(s)",
        font=get_font(9),
        foreground=COLORS['muted']
    )
    backup_count_label.pack(side=tk.RIGHT)
    
    return status_label, backup_count_label


def show_custom_dialog(parent, title: str, message: str, width: int = 600, height: int = 400):
    """Show a custom dialog with scrollable content."""
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center on parent
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - width) // 2
    y = parent.winfo_y() + (parent.winfo_height() - height) // 2
    dialog.geometry(f"+{x}+{y}")
    
    frame = ttk.Frame(dialog, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # Scrollable text
    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=get_font(10, mono=True),
        padx=SPACING['md'],
        pady=SPACING['md']
    )
    text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
    text_widget.insert('1.0', message)
    text_widget.configure(state=tk.DISABLED)
    
    # OK button
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill=tk.X)
    
    if HAS_TTK_BOOTSTRAP:
        ttk.Button(
            btn_frame,
            text="Close",
            command=dialog.destroy,
            bootstyle="primary",
            width=12
        ).pack(side=tk.RIGHT)
    else:
        ttk.Button(
            btn_frame,
            text="Close",
            command=dialog.destroy,
            width=12
        ).pack(side=tk.RIGHT)
    
    dialog.bind('<Escape>', lambda e: dialog.destroy())
    dialog.bind('<Return>', lambda e: dialog.destroy())


def show_about_dialog(parent):
    """Show the about dialog."""
    def get_rclone_version():
        try:
            result = subprocess.run(
                ['rclone', 'version'],
                capture_output=True,
                text=True,
                timeout=3
            )
            if result.returncode == 0:
                return result.stdout.split('\n')[0].replace('rclone ', '')
            return 'installed'
        except Exception:
            return 'not found'
    
    about_text = f"""
{APP_NAME}
Version {VERSION}

Created by {AUTHOR}

A modern, user-friendly interface for managing rclone backup operations.
No command line required.

FEATURES
{'-'*40}
{ICONS['success']} Visual backup management
{ICONS['clock']} Automatic scheduling
{ICONS['sync']} Real-time progress tracking
{ICONS['minimize']} System tray integration
{ICONS['settings']} Easy configuration

SYSTEM INFO
{'-'*40}
Platform: {platform.system()} {platform.release()}
Python: {platform.python_version()}
rclone: {get_rclone_version()}

FILES
{'-'*40}
Config: {CFG_FILE}
Logs: {LOG_FILE}

LINKS
{'-'*40}
GitHub: {GITHUB_REPO}
Issues: {GITHUB_REPO}/issues

LICENSE
{'-'*40}
Source Available - Free for personal use
"""
    show_custom_dialog(parent, "About", about_text.strip())


def show_documentation_dialog(parent):
    """Show documentation dialog."""
    doc_text = f"""
RClone Backup Manager - Documentation

QUICK START
{'-'*50}
1. Go to Configuration tab
2. Click "Add New Backup" to create a backup set
3. Select local folder and enter remote path
4. Save changes
5. Go to Backups tab and click "Start All"

BACKUP OPERATIONS
{'-'*50}
{ICONS['play']} Start All      - Run all backups immediately
{ICONS['bolt']} Run Once       - Run backups with completion notification  
{ICONS['minimize']} Minimize       - Hide to system tray

CONFIGURATION OPTIONS
{'-'*50}
Transfers   - Number of parallel file transfers (default: 8)
Checkers    - Number of parallel file checkers (default: 8)
Retries     - Number of retries on failure (default: 3)
Dry Run     - Test without copying files
Auto-Run    - Automatic backup every 5 minutes
Start Minimized - Start hidden in system tray

REMOTE PATH FORMAT
{'-'*50}
Format: remotename:path/to/folder

Examples:
  gdrive:Backups/Documents
  onedrive:MyBackups
  s3:mybucket/backups

KEYBOARD SHORTCUTS
{'-'*50}
F5          Reload configuration
Ctrl+Q      Exit application
Escape      Close dialogs

TIPS
{'-'*50}
{ICONS['info']} First backup uses checksum for accuracy
{ICONS['info']} Logs auto-refresh every 2 seconds
{ICONS['info']} Use "Run Once" for one-time backups with notification
{ICONS['info']} System tray keeps app running in background
"""
    show_custom_dialog(parent, "Documentation", doc_text.strip(), 650, 500)


def show_shortcuts_dialog(parent):
    """Show keyboard shortcuts dialog."""
    shortcuts_text = f"""
KEYBOARD SHORTCUTS
{'='*40}

GLOBAL
{'-'*40}
F5              Reload configuration
Ctrl+Q          Exit application

DIALOGS
{'-'*40}
Escape          Close dialog
Enter           Confirm/OK

NAVIGATION
{'-'*40}
Tab             Next field
Shift+Tab       Previous field
Ctrl+Tab        Next tab
Ctrl+Shift+Tab  Previous tab
"""
    show_custom_dialog(parent, "Keyboard Shortcuts", shortcuts_text.strip(), 400, 350)
