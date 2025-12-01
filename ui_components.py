#!/usr/bin/env python3
"""Reusable UI components and helper functions."""

import platform
import subprocess
import sys
from typing import Dict, Tuple, TYPE_CHECKING

from constants import (
    APP_NAME, VERSION, AUTHOR, GITHUB_REPO,
    CFG_FILE, LOG_FILE, HAS_TRAY, HAS_TTK_BOOTSTRAP,
    ttk, messagebox, scrolledtext
)

if TYPE_CHECKING:
    if HAS_TTK_BOOTSTRAP:
        from ttkbootstrap import Window
    else:
        import tkinter as tk


def create_tooltip(widget, text: str):
    """Create a tooltip for a widget."""
    if HAS_TTK_BOOTSTRAP:
        from ttkbootstrap.tooltip import ToolTip
        ToolTip(widget, text=text)
    else:
        pass


def create_menu_bar(root, callbacks: Dict):
    """Create the application menu bar."""
    import tkinter as tk
    menubar = tk.Menu(root)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(
        label="Reload Config",
        command=callbacks.get('reload_config'),
        accelerator="F5"
    )
    file_menu.add_command(
        label="View Config File",
        command=callbacks.get('view_config_file')
    )
    file_menu.add_command(
        label="View Log File",
        command=callbacks.get('view_log_file')
    )
    file_menu.add_separator()
    file_menu.add_command(
        label="Exit",
        command=callbacks.get('on_close'),
        accelerator="Ctrl+Q"
    )
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(
        label="Documentation",
        command=callbacks.get('show_documentation')
    )
    help_menu.add_command(
        label="Keyboard Shortcuts",
        command=callbacks.get('show_shortcuts')
    )
    help_menu.add_separator()
    help_menu.add_command(
        label="About",
        command=callbacks.get('show_about')
    )
    
    return menubar


def create_status_bar(parent, initial_text: str = "Ready") -> Tuple:
    """Create a status bar with main status and backup count labels."""
    import tkinter as tk
    status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
    status_frame.pack(side=tk.BOTTOM, fill=tk.X)
    
    status_label = ttk.Label(
        status_frame,
        text=initial_text,
        anchor=tk.W,
        padding=(5, 2)
    )
    status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    backup_count_label = ttk.Label(
        status_frame,
        text="0 backup(s) configured",
        anchor=tk.E,
        padding=(5, 2)
    )
    backup_count_label.pack(side=tk.RIGHT)
    
    return status_label, backup_count_label


def show_custom_dialog(parent, title: str, message: str):
    """Show a custom dialog with scrollable text."""
    import tkinter as tk
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.grab_set()
    
    frame = ttk.Frame(dialog, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    text_widget = scrolledtext.ScrolledText(
        frame,
        wrap=tk.WORD,
        font=('TkDefaultFont', 10),
        width=70,
        height=25,
        state=tk.NORMAL
    )
    text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    text_widget.insert('1.0', message)
    text_widget.config(state=tk.DISABLED)
    
    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill=tk.X)
    ttk.Button(
        btn_frame,
        text="OK",
        command=dialog.destroy,
        width=10
    ).pack(side=tk.RIGHT)
    
    dialog.update_idletasks()
    x = parent.winfo_x() + (parent.winfo_width() - dialog.winfo_width()) // 2
    y = parent.winfo_y() + (parent.winfo_height() - dialog.winfo_height()) // 2
    dialog.geometry(f"+{x}+{y}")
    
    dialog.bind('<Escape>', lambda e: dialog.destroy())


def show_about_dialog(parent):
    """Show the about dialog."""
    import tkinter as tk
    def get_rclone_version():
        try:
            result = subprocess.run(
                ['rclone', 'version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                first_line = result.stdout.split('\n')[0]
                return first_line.split()[1] if len(first_line.split()) > 1 else 'installed'
            return 'installed'
        except Exception:
            return 'not found'
    
    about_text = f"""{APP_NAME} v{VERSION}

A beautiful, production-ready cross-platform GUI for managing rclone backups
with modern tabbed interface and automated scheduling.

Made with ❤️ by {AUTHOR}

KEY FEATURES:
• Multi-threaded parallel backup operations
• Visual configuration editor
• Real-time progress tracking
• Last backup timestamp tracking
• Auto-run scheduler (every 5 minutes)
• System tray support
• Dry run mode
• Cross-platform (Windows & Linux)

SYSTEM INFORMATION:
Platform: {platform.system()} {platform.release()}
Python: {sys.version.split()[0]}
rclone: {get_rclone_version()}

CONFIG & LOGS:
Config: {CFG_FILE.name}
Logs: {LOG_FILE.name}

LINKS:
GitHub: {GITHUB_REPO}
Report Issues: {GITHUB_REPO}/issues
Documentation: {GITHUB_REPO}#readme

LICENSE:
Source Available License
Free for personal use. No commercial redistribution.
"""
    show_custom_dialog(parent, "About", about_text)


def show_documentation_dialog(parent):
    """Show the documentation dialog."""
    doc_text = f"""rclone Backup Manager - Quick Guide

BACKUP OPERATIONS:
• Start All Now - Run all configured backups immediately
• Run Once - Run backups and show completion notification
• Dry Run - Test backups without copying files
• Auto-Run - Automatically run backups every 5 minutes

CONFIGURATION:
• Add/Edit/Delete backup sets via GUI
• Browse folders easily
• All settings saved to folders.json

KEYBOARD SHORTCUTS:
• F5 - Reload configuration
• Ctrl+Q - Exit application

TIPS:
• First backup uses --checksum for accuracy
• Logs auto-refresh every 2 seconds
• Minimize to tray keeps app running in background
• Config file location: {CFG_FILE}
"""
    show_custom_dialog(parent, "Documentation", doc_text)


def show_shortcuts_dialog(parent):
    """Show the keyboard shortcuts dialog."""
    shortcuts_text = """Keyboard Shortcuts

F5           Reload Configuration
Ctrl+Q       Exit Application

Tab          Switch between tabs
Esc          Close dialogs
"""
    show_custom_dialog(parent, "Keyboard Shortcuts", shortcuts_text)
