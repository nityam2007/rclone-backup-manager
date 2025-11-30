#!/usr/bin/env python3
"""
RClone Backup Manager - Production-Ready Backup GUI
A beautiful, cross-platform GUI for managing your rclone backups with ease.

Author: Nityam (https://github.com/Nityam2007)
Repository: https://github.com/Nityam2007/rclone-backup-manager
License: Public Domain (Unlicense)
Version: 2.0.0

Features:
- Cross-platform (Windows & Linux)
- Modern tabbed interface with real-time progress tracking
- Visual configuration editor (no manual JSON editing)
- System tray support with minimize to tray
- Auto-run mode - backups every 5 minutes
- Last backup timestamp tracking
- Comprehensive logging with auto-refresh
- Dry run mode for testing
- Multi-threaded parallel operations
- Can be compiled to standalone executable
"""

import argparse
import json
import logging
import os
import platform
import re
import shlex
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# GUI imports
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext, filedialog
    HAS_TK = True
except ImportError:
    HAS_TK = False
    print("ERROR: tkinter not available. Please install python3-tk")
    sys.exit(1)

# System tray imports
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# Constants
VERSION = "2.0.0"
APP_NAME = "RClone Backup Manager"
GITHUB_REPO = "https://github.com/Nityam2007/rclone-backup-manager"
AUTHOR = "Nityam"

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

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

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


def load_config() -> Dict:
    """Load configuration from JSON file."""
    if not CFG_FILE.exists():
        default_config = {
            "backup_sets": [],
            "settings": {
                "transfers": 8,
                "checkers": 8,
                "retries": 3,
                "retries_sleep": "10s"
            },
            "app_settings": {
                "minimize_to_tray": True,
                "auto_run_enabled": False,
                "auto_run_interval_min": 5
            }
        }
        save_config(default_config)
        return default_config

    try:
        with CFG_FILE.open('r', encoding='utf-8') as f:
            config = json.load(f)

        # Ensure settings exist
        if 'settings' not in config:
            config['settings'] = {
                "transfers": 8,
                "checkers": 8,
                "retries": 3,
                "retries_sleep": "10s"
            }

        # Ensure app_settings exist
        if 'app_settings' not in config:
            config['app_settings'] = {
                "minimize_to_tray": True,
                "auto_run_enabled": False,
                "auto_run_interval_min": 5
            }

        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {
            "backup_sets": [],
            "settings": {},
            "app_settings": {
                "minimize_to_tray": True,
                "auto_run_enabled": False,
                "auto_run_interval_min": 5
            }
        }


def save_config(config: Dict) -> bool:
    """Save configuration to JSON file."""
    try:
        with CFG_FILE.open('w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


def run_rclone_copy(
    local: str,
    remote: str,
    extras: List[str],
    progress_callback=None,
    log_callback=None
) -> int:
    """Execute rclone copy with progress tracking."""
    cmd = ['rclone', 'copy', local, remote, '--progress'] + extras

    if IS_WINDOWS:
        # Windows-specific handling
        cmd_str = subprocess.list2cmdline(cmd)
    else:
        cmd_str = ' '.join(shlex.quote(x) for x in cmd)

    logger.info(f'Running: {cmd_str}')
    if log_callback:
        log_callback(f'Command: {cmd_str}\n')

    try:
        # Use different encoding on Windows
        encoding = 'utf-8' if not IS_WINDOWS else 'cp437'

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=encoding,
            errors='replace'
        )

        percent = 0.0
        for line in p.stdout:
            line = line.rstrip('\n')
            if log_callback:
                log_callback(line + '\n')

            if progress_callback:
                # Try to extract percentage
                m = re.search(r'(\d{1,3})%', line)
                if m:
                    try:
                        percent = float(m.group(1))
                    except ValueError:
                        pass
                progress_callback(percent, line)

        rc = p.wait()
        if progress_callback:
            progress_callback(100.0, f'Finished (exit code: {rc})')
        if log_callback:
            log_callback(f'\n=== Finished with exit code: {rc} ===\n\n')

        return rc

    except FileNotFoundError:
        error_msg = "ERROR: rclone not found. Please install rclone and ensure it's in PATH"
        logger.error(error_msg)
        if log_callback:
            log_callback(error_msg + '\n')
        if progress_callback:
            progress_callback(0, error_msg)
        return 127
    except Exception as e:
        error_msg = f'ERROR: {e}'
        logger.exception(error_msg)
        if log_callback:
            log_callback(error_msg + '\n')
        if progress_callback:
            progress_callback(percent, error_msg)
        return 1


class BackupManager:
    """Manages backup operations and tracks their status."""

    def __init__(self):
        self.config = load_config()
        self.threads: Dict[str, threading.Thread] = {}
        self.status: Dict[str, Dict] = {}
        self.logs: Dict[str, List[str]] = {}
        self.last_run_times: Dict[str, str] = {}  # Store last run timestamps
        self.lock = threading.Lock()
        self.stop_requested = False

    def reload_config(self):
        """Reload configuration from file."""
        self.config = load_config()
        logger.info("Configuration reloaded")

    def get_backup_sets(self) -> List[Dict]:
        """Get list of backup sets."""
        return self.config.get('backup_sets', [])

    def get_settings(self) -> Dict:
        """Get settings."""
        return self.config.get('settings', {})

    def start_all(self, dry_run: bool = False):
        """Start all backup operations."""
        self.stop_requested = False
        settings = self.get_settings()

        # Build extras from settings
        extras = [
            f'--transfers={settings.get("transfers", 8)}',
            f'--checkers={settings.get("checkers", 8)}',
            f'--retries={settings.get("retries", 3)}',
            f'--retries-sleep={settings.get("retries_sleep", "10s")}'
        ]

        # First run uses checksum
        first_run = not FIRST_RUN_FLAG.exists()
        if first_run:
            extras.append('--checksum')
            logger.info("First run detected, using --checksum")

        if dry_run:
            extras.append('--dry-run')

        for backup_set in self.get_backup_sets():
            name = backup_set.get('name', 'unnamed')
            local = backup_set.get('local', '')
            remote = backup_set.get('remote', '')

            if not local or not remote:
                logger.warning(f"Skipping {name}: missing local or remote path")
                continue

            # Clear previous status and logs
            with self.lock:
                self.status[name] = {'percent': 0, 'line': 'Starting...', 'rc': None}
                self.logs[name] = []

            t = threading.Thread(
                target=self._run_backup,
                args=(name, local, remote, extras),
                daemon=True
            )
            self.threads[name] = t
            t.start()

        if first_run:
            FIRST_RUN_FLAG.write_text(datetime.utcnow().isoformat())

    def _run_backup(self, name: str, local: str, remote: str, extras: List[str]):
        """Run a single backup operation."""
        # Record start time
        start_time = datetime.now()
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

        def progress_cb(percent, line):
            with self.lock:
                self.status[name] = {'percent': percent, 'line': line, 'rc': None}

        def log_cb(line):
            with self.lock:
                self.logs[name].append(line)

        # Log start time
        with self.lock:
            self.logs[name].append(f'\n=== Backup started at {start_time_str} ===\n')

        # Adjust remote path if needed
        try:
            rhs_raw = remote.split(':', 1)[1] if ':' in remote else ''
        except Exception:
            rhs_raw = ''

        # If remote has no path after colon, append local folder name
        if '/' not in rhs_raw and rhs_raw:
            target_remote = f"{remote.rstrip('/')}/{Path(local).name}"
        else:
            target_remote = remote

        logger.info(f"Starting backup: {name} ({local} -> {target_remote}) at {start_time_str}")
        rc = run_rclone_copy(local, target_remote, extras, progress_cb, log_cb)

        # Record completion time
        end_time = datetime.now()
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        duration = (end_time - start_time).total_seconds()

        with self.lock:
            self.status[name] = {
                'percent': 100.0,
                'line': f'Completed (exit code: {rc})',
                'rc': rc
            }
            self.last_run_times[name] = end_time_str
            self.logs[name].append(f'\n=== Backup completed at {end_time_str} (duration: {duration:.1f}s) ===\n')

        logger.info(f"Backup completed: {name} (exit code: {rc}) at {end_time_str}")

    def get_status(self) -> Dict:
        """Get current status of all backups."""
        with self.lock:
            return dict(self.status)

    def get_logs(self, name: str) -> str:
        """Get logs for a specific backup."""
        with self.lock:
            return ''.join(self.logs.get(name, []))

    def get_last_run_time(self, name: str) -> str:
        """Get last run time for a specific backup."""
        with self.lock:
            return self.last_run_times.get(name, 'Never')

    def is_running(self) -> bool:
        """Check if any backup is currently running."""
        status = self.get_status()
        for name, s in status.items():
            if s.get('rc') is None and s.get('percent', 0) < 100:
                return True
        return False


class MainWindow:
    """Main application window with tabbed interface."""

    def __init__(self, manager: BackupManager):
        self.manager = manager
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        # Set window icon if available (using PIL to create a simple icon)
        try:
            if HAS_TRAY:
                icon_img = Image.new('RGB', (32, 32), color=(0, 120, 215))
                draw = ImageDraw.Draw(icon_img)
                draw.rectangle((4, 4, 28, 28), fill=(255, 255, 255))
                draw.text((8, 8), "R", fill=(0, 120, 215))
                # Convert to PhotoImage for tkinter
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, photo)
        except:
            pass

        # Load app settings from config
        app_settings = self.manager.config.get('app_settings', {})

        # Tray icon reference
        self.tray_icon = None
        self.is_minimized_to_tray = False
        self.minimize_to_tray_enabled = tk.BooleanVar(
            value=app_settings.get('minimize_to_tray', True)
        )

        # Auto-run timer
        self.auto_run_enabled = tk.BooleanVar(
            value=app_settings.get('auto_run_enabled', False)
        )
        self.auto_run_timer = None
        self.initial_delay_timer = None

        # Setup UI
        self._setup_ui()
        self._setup_tray()

        # Handle window close and minimize
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Unmap>", self._on_minimize)

        # Start status update loop
        self._update_status()

        # Auto-refresh logs
        self._auto_refresh_logs()

        # Start auto-run if enabled
        if self.auto_run_enabled.get():
            self._toggle_auto_run()

    def _setup_ui(self):
        """Setup the main UI components."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reload Config", command=self._reload_config, accelerator="F5")
        file_menu.add_command(label="View Config File", command=self._view_config_file)
        file_menu.add_command(label="View Log File", command=self._view_log_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close, accelerator="Ctrl+Q")

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)

        # Bind keyboard shortcuts
        self.root.bind('<F5>', lambda e: self._reload_config())
        self.root.bind('<Control-q>', lambda e: self._on_close())

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Backup Operations
        self.backup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.backup_tab, text="Backups")
        self._setup_backup_tab()

        # Tab 2: Configuration Editor
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Configuration")
        self._setup_config_tab()

        # Tab 3: Logs
        self.logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_tab, text="Logs")
        self._setup_logs_tab()

        # Status bar with better styling
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_bar = ttk.Label(
            status_frame,
            text="Ready",
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Add backup count indicator
        backup_count = len(self.manager.get_backup_sets())
        self.backup_count_label = ttk.Label(
            status_frame,
            text=f"{backup_count} backup(s) configured",
            anchor=tk.E,
            padding=(5, 2)
        )
        self.backup_count_label.pack(side=tk.RIGHT)

    def _setup_backup_tab(self):
        """Setup the backup operations tab."""
        # Top button bar
        btn_frame = ttk.Frame(self.backup_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            btn_frame,
            text="Start All Now",
            command=self._start_all
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            btn_frame,
            text="Run Once",
            command=self._run_once
        ).pack(side=tk.LEFT, padx=2)

        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_frame,
            text="Dry Run",
            variable=self.dry_run_var
        ).pack(side=tk.LEFT, padx=2)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Auto-run checkbox
        ttk.Checkbutton(
            btn_frame,
            text="Auto-Run Every 5 Min",
            variable=self.auto_run_enabled,
            command=self._toggle_auto_run
        ).pack(side=tk.LEFT, padx=2)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(
            btn_frame,
            text="Reload Config",
            command=self._reload_config
        ).pack(side=tk.LEFT, padx=2)

        if HAS_TRAY:
            ttk.Checkbutton(
                btn_frame,
                text="Minimize to Tray",
                variable=self.minimize_to_tray_enabled,
                command=self._save_app_settings
            ).pack(side=tk.LEFT, padx=2)

        # Backup sets display
        list_frame = ttk.LabelFrame(self.backup_tab, text="Backup Sets", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollable canvas for backup items
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.backup_items_frame = ttk.Frame(canvas)

        self.backup_items_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.backup_items_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Widgets dictionary
        self.backup_widgets = {}

        # Initial load
        self._refresh_backup_list()

    def _setup_config_tab(self):
        """Setup the configuration editor tab."""
        # Toolbar
        toolbar = ttk.Frame(self.config_tab)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(
            toolbar,
            text="Add New Backup",
            command=self._add_backup_dialog
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="Save All Changes",
            command=self._save_config_from_form
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(
            toolbar,
            text=f"Config: {CFG_FILE.name}"
        ).pack(side=tk.RIGHT, padx=5)

        # Settings frame
        settings_frame = ttk.LabelFrame(self.config_tab, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # Settings fields
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill=tk.X)

        ttk.Label(settings_grid, text="Transfers:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.transfers_var = tk.StringVar(value="8")
        ttk.Entry(settings_grid, textvariable=self.transfers_var, width=10).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(settings_grid, text="Checkers:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.checkers_var = tk.StringVar(value="8")
        ttk.Entry(settings_grid, textvariable=self.checkers_var, width=10).grid(row=0, column=3, sticky=tk.W)

        ttk.Label(settings_grid, text="Retries:").grid(row=0, column=4, sticky=tk.W, padx=(20, 5))
        self.retries_var = tk.StringVar(value="3")
        ttk.Entry(settings_grid, textvariable=self.retries_var, width=10).grid(row=0, column=5, sticky=tk.W)

        # Backup sets list frame
        list_frame = ttk.LabelFrame(self.config_tab, text="Configured Backups", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollable canvas
        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.config_items_frame = ttk.Frame(canvas)

        self.config_items_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.config_items_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load initial content
        self._load_config_to_form()

    def _setup_logs_tab(self):
        """Setup the logs viewer tab."""
        # Toolbar
        toolbar = ttk.Frame(self.logs_tab)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(toolbar, text="Select Backup:").pack(side=tk.LEFT, padx=2)

        self.log_selector = ttk.Combobox(toolbar, state='readonly', width=30)
        self.log_selector.pack(side=tk.LEFT, padx=2)
        self.log_selector.bind('<<ComboboxSelected>>', self._load_selected_log)

        ttk.Button(
            toolbar,
            text="Refresh",
            command=self._refresh_log_selector
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="Clear",
            command=self._clear_log_view
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="View Log File",
            command=self._view_log_file
        ).pack(side=tk.LEFT, padx=2)

        # Log viewer
        log_frame = ttk.Frame(self.logs_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_viewer = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9) if IS_WINDOWS else ('Monospace', 9),
            state=tk.DISABLED
        )
        self.log_viewer.pack(fill=tk.BOTH, expand=True)

        self._refresh_log_selector()

    def _setup_tray(self):
        """Setup system tray icon."""
        if not HAS_TRAY:
            return

        # Create icon image
        img = Image.new('RGB', (64, 64), color=(0, 120, 215))
        draw = ImageDraw.Draw(img)
        draw.rectangle((8, 8, 56, 56), fill=(255, 255, 255))
        draw.text((16, 20), "RB", fill=(0, 120, 215))

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show", self._restore_from_tray, default=True),
            pystray.MenuItem("Start Backups", self._start_all),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._quit_app)
        )

        self.tray_icon = pystray.Icon(
            "rclone_backup",
            img,
            APP_NAME,
            menu
        )

    def _refresh_backup_list(self):
        """Refresh the list of backup sets."""
        # Clear existing widgets
        for widget in self.backup_items_frame.winfo_children():
            widget.destroy()

        self.backup_widgets.clear()

        backup_sets = self.manager.get_backup_sets()

        if not backup_sets:
            ttk.Label(
                self.backup_items_frame,
                text="No backup sets configured. Add them in the Configuration tab.",
                foreground="gray"
            ).pack(pady=20)
            return

        for idx, backup_set in enumerate(backup_sets):
            name = backup_set.get('name', 'unnamed')
            local = backup_set.get('local', '')
            remote = backup_set.get('remote', '')

            # Frame for this backup set
            item_frame = ttk.LabelFrame(
                self.backup_items_frame,
                text=name,
                padding=10
            )
            item_frame.pack(fill=tk.X, padx=5, pady=5)

            # Info labels
            info_frame = ttk.Frame(item_frame)
            info_frame.pack(fill=tk.X)

            ttk.Label(info_frame, text="Local:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=(0, 5)
            )
            ttk.Label(info_frame, text=local, foreground="blue").grid(
                row=0, column=1, sticky=tk.W
            )

            ttk.Label(info_frame, text="Remote:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=(0, 5)
            )
            ttk.Label(info_frame, text=remote, foreground="green").grid(
                row=1, column=1, sticky=tk.W
            )

            # Last run time
            ttk.Label(info_frame, text="Last Run:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=2, column=0, sticky=tk.W, padx=(0, 5)
            )
            last_run_label = ttk.Label(info_frame, text="Never", foreground="gray")
            last_run_label.grid(row=2, column=1, sticky=tk.W)

            # Progress bar
            progress = ttk.Progressbar(
                item_frame,
                orient=tk.HORIZONTAL,
                length=400,
                mode='determinate'
            )
            progress.pack(fill=tk.X, pady=(5, 0))

            # Status label
            status_label = ttk.Label(
                item_frame,
                text="Idle",
                foreground="gray"
            )
            status_label.pack(fill=tk.X)

            self.backup_widgets[name] = {
                'progress': progress,
                'status': status_label,
                'last_run': last_run_label
            }

    def _update_status(self):
        """Update status of all backup operations."""
        status = self.manager.get_status()

        for name, widgets in self.backup_widgets.items():
            s = status.get(name)
            if s:
                percent = s.get('percent', 0)
                line = s.get('line', '')
                rc = s.get('rc')

                widgets['progress']['value'] = percent

                # Color code status
                if rc is not None:
                    if rc == 0:
                        widgets['status'].config(text=line, foreground="green")
                    else:
                        widgets['status'].config(text=line, foreground="red")
                else:
                    widgets['status'].config(text=line, foreground="black")
            else:
                widgets['status'].config(text="Idle", foreground="gray")

            # Update last run time
            last_run = self.manager.get_last_run_time(name)
            if last_run != 'Never':
                widgets['last_run'].config(text=last_run, foreground="blue")
            else:
                widgets['last_run'].config(text=last_run, foreground="gray")

        # Update status bar
        if self.manager.is_running():
            self.status_bar.config(text="Backups in progress...")
        else:
            self.status_bar.config(text="Ready")

        # Schedule next update
        self.root.after(1000, self._update_status)

    def _start_all(self):
        """Start all backups."""
        if self.manager.is_running():
            messagebox.showwarning("Already Running", "Backups are already in progress.")
            return

        dry_run = self.dry_run_var.get()
        self.manager.start_all(dry_run=dry_run)
        self.status_bar.config(text="Backups started...")

    def _run_once(self):
        """Run backups once and show completion dialog."""
        if self.manager.is_running():
            messagebox.showwarning("Already Running", "Backups are already in progress.")
            return

        dry_run = self.dry_run_var.get()
        self.manager.start_all(dry_run=dry_run)

        # Monitor in background
        def monitor():
            names = [s.get('name') for s in self.manager.get_backup_sets()]
            while True:
                st = self.manager.get_status()
                if all((st.get(n) and st.get(n).get('rc') is not None) for n in names):
                    break
                time.sleep(0.5)

            # Show summary
            st = self.manager.get_status()
            ok = [n for n, v in st.items() if v.get('rc') == 0]
            fail = [n for n, v in st.items() if v.get('rc') not in (0, None)]

            msg = f"Backup completed!\n\nSuccessful: {len(ok)}\nFailed: {len(fail)}"
            if fail:
                msg += f"\n\nFailed backups:\n" + "\n".join(f"  - {n}" for n in fail)

            self.root.after(0, lambda: messagebox.showinfo("Backup Complete", msg))

        threading.Thread(target=monitor, daemon=True).start()

    def _reload_config(self):
        """Reload configuration."""
        self.manager.reload_config()
        self._refresh_backup_list()
        self._load_config_to_form()
        self._refresh_log_selector()

        # Update backup count
        backup_count = len(self.manager.get_backup_sets())
        self.backup_count_label.config(text=f"{backup_count} backup(s) configured")

        messagebox.showinfo("Reloaded", "Configuration reloaded successfully.")

    def _load_config_to_form(self):
        """Load config into the form-based UI."""
        config = self.manager.config
        settings = config.get('settings', {})

        # Load settings
        self.transfers_var.set(str(settings.get('transfers', 8)))
        self.checkers_var.set(str(settings.get('checkers', 8)))
        self.retries_var.set(str(settings.get('retries', 3)))

        # Clear existing backup items
        for widget in self.config_items_frame.winfo_children():
            widget.destroy()

        # Load backup sets
        backup_sets = config.get('backup_sets', [])
        if not backup_sets:
            ttk.Label(
                self.config_items_frame,
                text="No backups configured. Click 'Add New Backup' to start.",
                foreground="gray"
            ).pack(pady=20)
            return

        for backup_set in backup_sets:
            self._add_backup_item_to_form(backup_set)

    def _add_backup_item_to_form(self, backup_set):
        """Add a backup item to the configuration form."""
        name = backup_set.get('name', '')
        local = backup_set.get('local', '')
        remote = backup_set.get('remote', '')

        # Frame for this backup
        item_frame = ttk.LabelFrame(self.config_items_frame, text=name, padding=10)
        item_frame.pack(fill=tk.X, padx=5, pady=5)

        # Fields
        fields_frame = ttk.Frame(item_frame)
        fields_frame.pack(fill=tk.X, side=tk.LEFT, expand=True)

        ttk.Label(fields_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        name_var = tk.StringVar(value=name)
        ttk.Entry(fields_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky=tk.EW, padx=5)

        ttk.Label(fields_frame, text="Local:").grid(row=1, column=0, sticky=tk.W, padx=5)
        local_var = tk.StringVar(value=local)
        local_entry = ttk.Entry(fields_frame, textvariable=local_var, width=50)
        local_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Button(
            fields_frame,
            text="Browse",
            command=lambda: self._browse_folder(local_var),
            width=8
        ).grid(row=1, column=2, padx=5)

        ttk.Label(fields_frame, text="Remote:").grid(row=2, column=0, sticky=tk.W, padx=5)
        remote_var = tk.StringVar(value=remote)
        ttk.Entry(fields_frame, textvariable=remote_var, width=50).grid(row=2, column=1, sticky=tk.EW, padx=5)

        fields_frame.columnconfigure(1, weight=1)

        # Delete button
        ttk.Button(
            item_frame,
            text="Delete",
            command=lambda: self._delete_backup_item(item_frame),
            width=8
        ).pack(side=tk.RIGHT, padx=5)

        # Store variables for later retrieval
        item_frame.name_var = name_var
        item_frame.local_var = local_var
        item_frame.remote_var = remote_var

    def _browse_folder(self, var):
        """Browse for folder."""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)

    def _delete_backup_item(self, frame):
        """Delete a backup item from the form."""
        if messagebox.askyesno("Confirm Delete", "Delete this backup configuration?"):
            frame.destroy()

    def _add_backup_dialog(self):
        """Show dialog to add new backup."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Backup")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Local Folder:").grid(row=1, column=0, sticky=tk.W, pady=5)
        local_var = tk.StringVar()
        ttk.Entry(frame, textvariable=local_var, width=40).grid(row=1, column=1, sticky=tk.EW, pady=5)
        ttk.Button(
            frame,
            text="Browse",
            command=lambda: self._browse_folder(local_var)
        ).grid(row=1, column=2, padx=5)

        ttk.Label(frame, text="Remote Path:").grid(row=2, column=0, sticky=tk.W, pady=5)
        remote_var = tk.StringVar()
        ttk.Entry(frame, textvariable=remote_var, width=40).grid(row=2, column=1, sticky=tk.EW, pady=5)

        ttk.Label(
            frame,
            text="Example: myremote:bucket/path",
            foreground="gray",
            font=('TkDefaultFont', 8)
        ).grid(row=3, column=1, sticky=tk.W)

        frame.columnconfigure(1, weight=1)

        def add_backup():
            if not name_var.get() or not local_var.get() or not remote_var.get():
                messagebox.showwarning("Missing Fields", "Please fill all fields.")
                return

            backup_set = {
                'name': name_var.get(),
                'local': local_var.get(),
                'remote': remote_var.get()
            }
            self._add_backup_item_to_form(backup_set)
            dialog.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=20)

        ttk.Button(btn_frame, text="Add", command=add_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _save_config_from_form(self):
        """Save configuration from form fields."""
        try:
            # Collect settings
            settings = {
                'transfers': int(self.transfers_var.get()),
                'checkers': int(self.checkers_var.get()),
                'retries': int(self.retries_var.get()),
                'retries_sleep': '10s'
            }

            # Collect backup sets
            backup_sets = []
            for item_frame in self.config_items_frame.winfo_children():
                if hasattr(item_frame, 'name_var'):
                    backup_sets.append({
                        'name': item_frame.name_var.get(),
                        'local': item_frame.local_var.get(),
                        'remote': item_frame.remote_var.get()
                    })

            # Collect app settings
            app_settings = {
                'minimize_to_tray': self.minimize_to_tray_enabled.get(),
                'auto_run_enabled': self.auto_run_enabled.get(),
                'auto_run_initial_delay_min': 20,
                'auto_run_interval_min': 5
            }

            config = {
                'backup_sets': backup_sets,
                'settings': settings,
                'app_settings': app_settings
            }

            if save_config(config):
                self.manager.config = config
                self._refresh_backup_list()
                messagebox.showinfo("Saved", "Configuration saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save configuration.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your settings values:\n{e}")

    def _refresh_log_selector(self):
        """Refresh the log selector dropdown."""
        names = [s.get('name') for s in self.manager.get_backup_sets()]
        self.log_selector['values'] = names
        if names and not self.log_selector.get():
            self.log_selector.current(0)
            self._load_selected_log(None)

    def _load_selected_log(self, event):
        """Load the selected backup's log."""
        name = self.log_selector.get()
        if not name:
            return

        logs = self.manager.get_logs(name)

        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.delete('1.0', tk.END)
        self.log_viewer.insert('1.0', logs if logs else "No logs available yet.")
        self.log_viewer.config(state=tk.DISABLED)
        self.log_viewer.see(tk.END)

    def _clear_log_view(self):
        """Clear the log viewer."""
        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.delete('1.0', tk.END)
        self.log_viewer.config(state=tk.DISABLED)

    def _view_log_file(self):
        """Open the main log file."""
        if not LOG_FILE.exists():
            messagebox.showinfo("No Log File", "Log file does not exist yet.")
            return

        # Open in default text editor
        if IS_WINDOWS:
            os.startfile(LOG_FILE)
        else:
            subprocess.Popen(['xdg-open', str(LOG_FILE)])

    def _on_minimize(self, event):
        """Handle window minimize event."""
        # Only respond to iconify events
        if event.type == "18" and self.minimize_to_tray_enabled.get():  # 18 is Unmap event type
            if HAS_TRAY and self.tray_icon and not self.is_minimized_to_tray:
                self.root.withdraw()
                self.is_minimized_to_tray = True

                # Run tray icon in background thread if not already running
                if not hasattr(self.tray_icon, '_running') or not self.tray_icon._running:
                    threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _restore_from_tray(self, icon=None, item=None):
        """Restore window from tray."""
        self.root.deiconify()
        self.root.lift()
        self.is_minimized_to_tray = False

    def _toggle_auto_run(self):
        """Toggle auto-run timer."""
        # Save setting to config
        self._save_app_settings()

        if self.auto_run_enabled.get():
            # Get interval from config
            app_settings = self.manager.config.get('app_settings', {})
            interval_min = app_settings.get('auto_run_interval_min', 5)

            logger.info(f"Auto-run enabled: Running every {interval_min} minutes")
            self.status_bar.config(text=f"Auto-run enabled: Running every {interval_min} minutes")

            # Start first backup immediately, then schedule recurring cycle
            self._start_auto_run_cycle()
        else:
            # Cancel timers
            logger.info("Auto-run disabled")
            if self.initial_delay_timer:
                self.root.after_cancel(self.initial_delay_timer)
                self.initial_delay_timer = None
            if self.auto_run_timer:
                self.root.after_cancel(self.auto_run_timer)
                self.auto_run_timer = None
            self.status_bar.config(text="Auto-run disabled")

    def _save_app_settings(self):
        """Save app settings (tray, auto-run) to config without user confirmation."""
        try:
            self.manager.config['app_settings'] = {
                'minimize_to_tray': self.minimize_to_tray_enabled.get(),
                'auto_run_enabled': self.auto_run_enabled.get(),
                'auto_run_interval_min': 5
            }
            save_config(self.manager.config)
        except Exception as e:
            logger.error(f"Failed to save app settings: {e}")

    def _start_auto_run_cycle(self):
        """Start the regular 5-minute auto-run cycle."""
        logger.info("Starting auto-run cycle")
        self._run_auto_backup()

        # Get interval from config
        app_settings = self.manager.config.get('app_settings', {})
        interval_min = app_settings.get('auto_run_interval_min', 5)
        interval_ms = interval_min * 60 * 1000

        # Schedule next run
        self.auto_run_timer = self.root.after(interval_ms, self._start_auto_run_cycle)

    def _run_auto_backup(self):
        """Run backup automatically."""
        if not self.manager.is_running():
            logger.info("Auto-run: Starting backup")
            self.manager.start_all(dry_run=False)
        else:
            logger.info("Auto-run: Backup already running, skipping")

    def _auto_refresh_logs(self):
        """Auto-refresh log viewer every 2 seconds."""
        # Only refresh if logs tab is active and a backup is selected
        try:
            if self.notebook.index(self.notebook.select()) == 2:  # Logs tab index
                current_log = self.log_selector.get()
                if current_log:
                    logs = self.manager.get_logs(current_log)
                    if logs:
                        self.log_viewer.config(state=tk.NORMAL)
                        current_pos = self.log_viewer.yview()
                        self.log_viewer.delete('1.0', tk.END)
                        self.log_viewer.insert('1.0', logs)
                        self.log_viewer.yview_moveto(current_pos[0])
                        self.log_viewer.config(state=tk.DISABLED)
        except:
            pass

        # Schedule next refresh
        self.root.after(2000, self._auto_refresh_logs)

    def _view_config_file(self):
        """Open the config file in default editor."""
        if not CFG_FILE.exists():
            messagebox.showinfo("No Config File", "Config file does not exist yet.")
            return

        try:
            if IS_WINDOWS:
                os.startfile(CFG_FILE)
            else:
                subprocess.Popen(['xdg-open', str(CFG_FILE)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open config file:\n{e}")

    def _show_documentation(self):
        """Show documentation dialog."""
        doc_text = """rclone Backup Manager - Quick Guide

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
• Config file location: {}
        """.format(CFG_FILE)

        self._show_custom_dialog("Documentation", doc_text)

    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """Keyboard Shortcuts

F5           Reload Configuration
Ctrl+Q       Exit Application

Tab          Switch between tabs
Esc          Close dialogs
        """
        self._show_custom_dialog("Keyboard Shortcuts", shortcuts_text)

    def _show_custom_dialog(self, title, message):
        """Show a custom dialog with proper font sizing."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with padding
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrolled text widget with normal font size
        text_widget = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=('TkDefaultFont', 10),
            width=70,
            height=25,
            state=tk.NORMAL
        )
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Insert message
        text_widget.insert('1.0', message)
        text_widget.config(state=tk.DISABLED)
        
        # OK button
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(
            btn_frame,
            text="OK",
            command=dialog.destroy,
            width=10
        ).pack(side=tk.RIGHT)
        
        # Center dialog on parent window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Bind Escape key to close
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def _show_about(self):
        """Show about dialog."""
        about_text = f"""{APP_NAME} v{VERSION}

A beautiful, production-ready cross-platform GUI for managing rclone backups
with modern tabbed interface and automated scheduling.

Made with ❤️ by {AUTHOR}

KEY FEATURES:
• Multi-threaded parallel backup operations
• Visual configuration editor (no manual JSON editing)
• Real-time progress tracking with detailed logs
• Last backup timestamp tracking
• Auto-run scheduler (every 5 minutes)
• System tray support (Windows & Ubuntu/GNOME)
• Dry run mode for testing backups
• Cross-platform (Windows & Linux)
• Single file architecture (~1450 lines)

SYSTEM INFORMATION:
Platform: {platform.system()} {platform.release()}
Python: {sys.version.split()[0]}
rclone: {self._get_rclone_version()}

CONFIG & LOGS:
Config: {CFG_FILE.name}
Logs: {LOG_FILE.name}

LINKS:
GitHub: {GITHUB_REPO}
Report Issues: {GITHUB_REPO}/issues
Documentation: {GITHUB_REPO}#readme

LICENSE:
Public Domain (Unlicense)
Use freely without restrictions.
"""
        self._show_custom_dialog("About", about_text)

    def _get_rclone_version(self):
        """Get rclone version."""
        try:
            result = subprocess.run(
                ['rclone', 'version'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Extract version from first line
                first_line = result.stdout.split('\n')[0]
                return first_line.split()[1] if len(first_line.split()) > 1 else 'installed'
            return 'installed'
        except:
            return 'not found'

    def _on_close(self):
        """Handle window close event."""
        if self.manager.is_running():
            if not messagebox.askokcancel(
                "Backups Running",
                "Backups are currently running. Are you sure you want to exit?"
            ):
                return

        self._quit_app()

    def _quit_app(self, icon=None, item=None):
        """Quit the application."""
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass

        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass

        sys.exit(0)

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'{APP_NAME} v{VERSION}'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file (default: folders.json in script directory)'
    )

    args = parser.parse_args()

    # Override config file if specified
    if args.config:
        global CFG_FILE
        CFG_FILE = Path(args.config).resolve()

    logger.info(f"Starting {APP_NAME} v{VERSION}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Config file: {CFG_FILE}")
    logger.info(f"Log file: {LOG_FILE}")

    # Check for tkinter
    if not HAS_TK:
        print("ERROR: tkinter not available. Please install python3-tk")
        sys.exit(1)

    # Warn if tray not available
    if not HAS_TRAY:
        logger.warning("pystray/Pillow not available. System tray disabled.")

    # Create backup manager
    manager = BackupManager()

    # Create and run GUI
    try:
        app = MainWindow(manager)
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
