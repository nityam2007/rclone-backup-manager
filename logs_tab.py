#!/usr/bin/env python3
"""Logs viewer tab UI and logic."""

import os
import subprocess
import tkinter as tk

from constants import ttk, scrolledtext, messagebox, IS_WINDOWS, LOG_FILE, HAS_TTK_BOOTSTRAP
from backup_manager import BackupManager
from ui_components import create_tooltip


class LogsTab:
    """Logs viewer tab component."""

    def __init__(self, parent: ttk.Frame, manager: BackupManager, root):
        self.parent = parent
        self.manager = manager
        self.root = root
        self.log_selector = None
        self.log_viewer = None

    def setup(self):
        """Setup the logs tab UI."""
        self._create_toolbar()
        self._create_log_viewer()
        self._refresh_log_selector()
        self._auto_refresh()

    def _create_toolbar(self):
        """Create the toolbar."""
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(toolbar, text="Select Backup:").pack(side=tk.LEFT, padx=2)

        self.log_selector = ttk.Combobox(toolbar, state='readonly', width=30)
        self.log_selector.pack(side=tk.LEFT, padx=2)
        self.log_selector.bind('<<ComboboxSelected>>', self._load_selected_log)
        create_tooltip(self.log_selector, "Select a backup to view its logs")

        refresh_btn = ttk.Button(
            toolbar,
            text="Refresh",
            command=self._refresh_log_selector
        )
        refresh_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(refresh_btn, "Refresh the list of backups")

        clear_btn = ttk.Button(
            toolbar,
            text="Clear",
            command=self._clear_log_view
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(clear_btn, "Clear the current log view")

        view_log_btn = ttk.Button(
            toolbar,
            text="View Log File",
            command=self._view_log_file
        )
        view_log_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(view_log_btn, "Open the main application log file")

    def _create_log_viewer(self):
        """Create the log viewer widget."""
        log_frame = ttk.Frame(self.parent)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.log_viewer = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=('Consolas', 9) if IS_WINDOWS else ('Monospace', 9),
            state=tk.DISABLED
        )
        self.log_viewer.pack(fill=tk.BOTH, expand=True)

    def _refresh_log_selector(self):
        """Refresh the log selector dropdown."""
        names = [s.get('name') for s in self.manager.get_backup_sets()]
        self.log_selector['values'] = names
        if names and not self.log_selector.get():
            self.log_selector.current(0)
            self._load_selected_log(None)

    def _load_selected_log(self, event):
        """Load the selected backup's log.
        
        Args:
            event: Event object (unused).
        """
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

    def _auto_refresh(self):
        """Auto-refresh log viewer every 2 seconds."""
        # Only refresh if logs tab is active and a backup is selected
        try:
            # Check if this tab is currently visible
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
        except Exception:
            pass

        # Schedule next refresh
        self.root.after(2000, self._auto_refresh)

    def reload(self):
        """Reload the log selector after configuration changes."""
        self._refresh_log_selector()
