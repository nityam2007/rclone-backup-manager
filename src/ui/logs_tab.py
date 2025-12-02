# Logs Tab | Python
"""Logs viewer tab with modern UI."""

import os
import subprocess
import tkinter as tk
from typing import Optional

from ..utils.constants import (
    ttk, scrolledtext, messagebox,
    IS_WINDOWS, LOG_FILE, HAS_TTK_BOOTSTRAP, COLORS
)
from ..core.backup_manager import BackupManager
from .components import create_tooltip
from .theme import ICONS


class LogsTab:
    """Modern logs viewer tab."""

    def __init__(self, parent: ttk.Frame, manager: BackupManager, root: tk.Tk):
        self.parent = parent
        self.manager = manager
        self.root = root
        self.log_selector: Optional[ttk.Combobox] = None
        self.log_viewer: Optional[scrolledtext.ScrolledText] = None
        self.auto_scroll_var = tk.BooleanVar(value=True)

    def setup(self):
        """Initialize the logs tab UI."""
        self._create_header()
        self._create_log_viewer()
        self._refresh_log_selector()
        self._start_auto_refresh()

    def _create_header(self):
        """Create the header with controls."""
        header = ttk.Frame(self.parent)
        header.pack(fill=tk.X, padx=15, pady=15)
        
        # Title
        ttk.Label(
            header,
            text=f"{ICONS['file']} Backup Logs",
            font=('Segoe UI', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        # Controls frame
        controls = ttk.Frame(header)
        controls.pack(side=tk.RIGHT)
        
        # Backup selector
        ttk.Label(controls, text="Select backup:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_selector = ttk.Combobox(controls, state='readonly', width=25)
        self.log_selector.pack(side=tk.LEFT, padx=(0, 15))
        self.log_selector.bind('<<ComboboxSelected>>', self._load_selected_log)
        create_tooltip(self.log_selector, "Select a backup to view its logs")
        
        # Action buttons
        if HAS_TTK_BOOTSTRAP:
            refresh_btn = ttk.Button(
                controls,
                text=f"{ICONS['refresh']}",
                command=self._refresh_log_selector,
                bootstyle="secondary-outline",
                width=4
            )
            refresh_btn.pack(side=tk.LEFT, padx=2)
            create_tooltip(refresh_btn, "Refresh backup list")
            
            clear_btn = ttk.Button(
                controls,
                text=f"{ICONS['delete']}",
                command=self._clear_log_view,
                bootstyle="secondary-outline",
                width=4
            )
            clear_btn.pack(side=tk.LEFT, padx=2)
            create_tooltip(clear_btn, "Clear log view")
            
            ttk.Separator(controls, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
            open_btn = ttk.Button(
                controls,
                text=f"{ICONS['external']} Open Log File",
                command=self._view_log_file,
                bootstyle="info-outline",
                width=14
            )
            open_btn.pack(side=tk.LEFT, padx=2)
            create_tooltip(open_btn, "Open main application log file")
        else:
            ttk.Button(controls, text="Refresh", command=self._refresh_log_selector, width=8).pack(side=tk.LEFT, padx=2)
            ttk.Button(controls, text="Clear", command=self._clear_log_view, width=8).pack(side=tk.LEFT, padx=2)
            ttk.Button(controls, text="Open Log", command=self._view_log_file, width=10).pack(side=tk.LEFT, padx=2)

    def _create_log_viewer(self):
        """Create the log viewer widget."""
        # Container frame
        viewer_frame = ttk.Labelframe(
            self.parent,
            text=f"{ICONS['file']} Log Output",
            padding=10
        )
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Options bar
        options_bar = ttk.Frame(viewer_frame)
        options_bar.pack(fill=tk.X, pady=(0, 10))
        
        if HAS_TTK_BOOTSTRAP:
            ttk.Checkbutton(
                options_bar,
                text="Auto-scroll to bottom",
                variable=self.auto_scroll_var,
                bootstyle="round-toggle"
            ).pack(side=tk.LEFT)
        else:
            ttk.Checkbutton(
                options_bar,
                text="Auto-scroll",
                variable=self.auto_scroll_var
            ).pack(side=tk.LEFT)
        
        # Log text widget
        self.log_viewer = scrolledtext.ScrolledText(
            viewer_frame,
            wrap=tk.WORD,
            font=('Consolas', 10) if IS_WINDOWS else ('Monospace', 10),
            state=tk.DISABLED,
            padx=10,
            pady=10,
            bg='#1e1e1e' if HAS_TTK_BOOTSTRAP else 'white',
            fg='#d4d4d4' if HAS_TTK_BOOTSTRAP else 'black',
            insertbackground='white'
        )
        self.log_viewer.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for syntax highlighting
        self.log_viewer.tag_configure('success', foreground='#4ec9b0')
        self.log_viewer.tag_configure('error', foreground='#f14c4c')
        self.log_viewer.tag_configure('warning', foreground='#cca700')
        self.log_viewer.tag_configure('info', foreground='#3794ff')
        self.log_viewer.tag_configure('header', foreground='#569cd6', font=('Consolas', 10, 'bold'))

    def _refresh_log_selector(self):
        """Refresh the backup selector dropdown."""
        names = [s.get('name') for s in self.manager.get_backup_sets()]
        self.log_selector['values'] = names
        
        if names:
            if not self.log_selector.get() or self.log_selector.get() not in names:
                self.log_selector.current(0)
            self._load_selected_log(None)
        else:
            self.log_selector.set('')
            self._show_no_backups_message()

    def _show_no_backups_message(self):
        """Show message when no backups are configured."""
        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.delete('1.0', tk.END)
        self.log_viewer.insert('1.0', 
            f"\n\n    {ICONS['info']} No backup sets configured.\n\n"
            f"    Go to Configuration tab to add backup sets.\n"
        )
        self.log_viewer.config(state=tk.DISABLED)

    def _load_selected_log(self, event):
        """Load logs for the selected backup."""
        name = self.log_selector.get()
        if not name:
            return
        
        logs = self.manager.get_logs(name)
        
        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.delete('1.0', tk.END)
        
        if logs:
            self._insert_highlighted_logs(logs)
        else:
            self.log_viewer.insert('1.0',
                f"\n    {ICONS['info']} No logs available for '{name}' yet.\n\n"
                f"    Logs will appear here when the backup runs.\n"
            )
        
        self.log_viewer.config(state=tk.DISABLED)
        
        if self.auto_scroll_var.get():
            self.log_viewer.see(tk.END)

    def _insert_highlighted_logs(self, logs: str):
        """Insert logs with syntax highlighting."""
        for line in logs.split('\n'):
            if '===' in line or line.startswith('Backup:') or line.startswith('Source:'):
                self.log_viewer.insert(tk.END, line + '\n', 'header')
            elif 'SUCCESS' in line or 'Completed' in line or 'exit code: 0' in line:
                self.log_viewer.insert(tk.END, line + '\n', 'success')
            elif 'ERROR' in line or 'FAILED' in line or 'error' in line.lower():
                self.log_viewer.insert(tk.END, line + '\n', 'error')
            elif 'WARNING' in line or 'warning' in line.lower():
                self.log_viewer.insert(tk.END, line + '\n', 'warning')
            elif line.startswith('$') or 'Transferring' in line:
                self.log_viewer.insert(tk.END, line + '\n', 'info')
            else:
                self.log_viewer.insert(tk.END, line + '\n')

    def _clear_log_view(self):
        """Clear the log viewer."""
        self.log_viewer.config(state=tk.NORMAL)
        self.log_viewer.delete('1.0', tk.END)
        self.log_viewer.config(state=tk.DISABLED)

    def _view_log_file(self):
        """Open the main application log file."""
        if not LOG_FILE.exists():
            messagebox.showinfo(
                "No Log File",
                "The log file doesn't exist yet.\nIt will be created when the application logs events."
            )
            return
        
        try:
            if IS_WINDOWS:
                os.startfile(LOG_FILE)
            else:
                subprocess.Popen(['xdg-open', str(LOG_FILE)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log file:\n{e}")

    def _start_auto_refresh(self):
        """Start automatic log refresh."""
        self._auto_refresh()

    def _auto_refresh(self):
        """Auto-refresh the log view."""
        try:
            current_log = self.log_selector.get()
            if current_log:
                logs = self.manager.get_logs(current_log)
                if logs:
                    # Check if content changed
                    self.log_viewer.config(state=tk.NORMAL)
                    current_content = self.log_viewer.get('1.0', tk.END).strip()
                    
                    if logs.strip() != current_content:
                        scroll_pos = self.log_viewer.yview()
                        self.log_viewer.delete('1.0', tk.END)
                        self._insert_highlighted_logs(logs)
                        
                        if self.auto_scroll_var.get():
                            self.log_viewer.see(tk.END)
                        else:
                            self.log_viewer.yview_moveto(scroll_pos[0])
                    
                    self.log_viewer.config(state=tk.DISABLED)
        except Exception:
            pass
        
        # Schedule next refresh
        self.root.after(2000, self._auto_refresh)

    def reload(self):
        """Reload the logs tab."""
        self._refresh_log_selector()
