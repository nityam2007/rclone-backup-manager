#!/usr/bin/env python3
"""Backup operations tab UI and logic.

This module implements the backup operations tab where users can
start backups, view progress, and manage auto-run settings.
"""

import threading
import time
from typing import Dict

from constants import ttk, messagebox, logger, HAS_TRAY, HAS_TTK_BOOTSTRAP
from backup_manager import BackupManager
from ui_components import create_tooltip


class BackupTab:
    """Backup operations tab component.
    
    This class handles:
    - Displaying backup sets with progress bars
    - Starting and monitoring backups
    - Auto-run scheduling
    - Status updates
    """

    def __init__(self, parent: ttk.Frame, manager: BackupManager, root):
        """Initialize the backup tab.
        
        Args:
            parent: Parent frame for this tab.
            manager: BackupManager instance.
            root: Root window for scheduling updates.
        """
        self.parent = parent
        self.manager = manager
        self.root = root
        self.backup_widgets: Dict[str, Dict] = {}
        
        # Variables
        import tkinter as tk
        self.dry_run_var = tk.BooleanVar(value=False)
        self.auto_run_enabled = tk.BooleanVar(
            value=manager.config.get('app_settings', {}).get('auto_run_enabled', False)
        )
        self.auto_run_timer = None
        self.initial_delay_timer = None
        
        # Status bar reference (set by main window)
        self.status_bar = None

    def setup(self):
        """Setup the backup tab UI."""
        self._create_toolbar()
        self._create_backup_list()
        self._refresh_backup_list()
        
        # Start status update loop
        self._update_status()
        
        # Start auto-run if enabled
        if self.auto_run_enabled.get():
            self._toggle_auto_run()

    def _create_toolbar(self):
        """Create the button toolbar with modern styling."""
        btn_frame = ttk.Frame(self.parent)
        btn_frame.pack(fill='x', padx=10, pady=10)

        # Modern styled buttons with colors
        if HAS_TTK_BOOTSTRAP:
            start_btn = ttk.Button(
                btn_frame,
                text="▶ Start All Now",
                command=self._start_all,
                bootstyle="success",  # Green button
                width=18
            )
            start_btn.pack(side='left', padx=5)
            create_tooltip(start_btn, "Start all configured backups immediately")

            run_once_btn = ttk.Button(
                btn_frame,
                text="⚡ Run Once",
                command=self._run_once,
                bootstyle="info",  # Blue button
                width=15
            )
            run_once_btn.pack(side='left', padx=5)
            create_tooltip(run_once_btn, "Run all backups once and notify on completion")

            dry_run_chk = ttk.Checkbutton(
                btn_frame,
                text="🔍 Dry Run",
                variable=self.dry_run_var,
                bootstyle="warning-round-toggle"  # Orange toggle
            )
            dry_run_chk.pack(side='left', padx=5)
            create_tooltip(dry_run_chk, "Simulate backups without copying files")
            
            ttk.Separator(btn_frame, orient='vertical').pack(side='left', fill='y', padx=10)

            auto_run_chk = ttk.Checkbutton(
                btn_frame,
                text="⏰ Auto-Run Every 5 Min",
                variable=self.auto_run_enabled,
                command=self._toggle_auto_run,
                bootstyle="primary-round-toggle"  # Blue toggle
            )
            auto_run_chk.pack(side='left', padx=5)
            create_tooltip(auto_run_chk, "Automatically run backups every 5 minutes")
        else:
            # Fallback to standard buttons
            import tkinter as tk
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

            ttk.Checkbutton(
                btn_frame,
                text="Dry Run",
                variable=self.dry_run_var
            ).pack(side=tk.LEFT, padx=2)

            ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

            ttk.Checkbutton(
                btn_frame,
                text="Auto-Run Every 5 Min",
                variable=self.auto_run_enabled,
                command=self._toggle_auto_run
            ).pack(side=tk.LEFT, padx=2)

    def _create_backup_list(self):
        """Create the backup sets display area."""
        import tkinter as tk
        list_frame = ttk.Labelframe(self.parent, text="📦 Backup Sets", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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

    def _refresh_backup_list(self):
        """Refresh the list of backup sets."""
        import tkinter as tk
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

        for backup_set in backup_sets:
            name = backup_set.get('name', 'unnamed')
            local = backup_set.get('local', '')
            remote = backup_set.get('remote', '')

            # Frame for this backup set
            item_frame = ttk.Labelframe(
                self.backup_items_frame,
                text=f"📁 {name}",
                padding=10
            )
            item_frame.pack(fill=tk.X, padx=5, pady=5)

            # Info labels
            info_frame = ttk.Frame(item_frame)
            info_frame.pack(fill=tk.X)

            ttk.Label(info_frame, text="💻 Local:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=0, column=0, sticky=tk.W, padx=(0, 5)
            )
            ttk.Label(info_frame, text=local, foreground="blue").grid(
                row=0, column=1, sticky=tk.W
            )

            ttk.Label(info_frame, text="☁️  Remote:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=1, column=0, sticky=tk.W, padx=(0, 5)
            )
            ttk.Label(info_frame, text=remote, foreground="green").grid(
                row=1, column=1, sticky=tk.W
            )

            # Last run time
            ttk.Label(info_frame, text="🕒 Last Run:", font=('TkDefaultFont', 9, 'bold')).grid(
                row=2, column=0, sticky=tk.W, padx=(0, 5)
            )
            last_run_label = ttk.Label(info_frame, text="Never", foreground="gray")
            last_run_label.grid(row=2, column=1, sticky=tk.W)

            # Progress bar
            if HAS_TTK_BOOTSTRAP:
                progress = ttk.Progressbar(
                    item_frame,
                    orient=tk.HORIZONTAL,
                    length=400,
                    mode='determinate',
                    bootstyle="success-striped"  # Striped green progress bar
                )
            else:
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
                        widgets['status'].config(text=f"✅ {line}", foreground="green")
                    else:
                        widgets['status'].config(text=f"❌ {line}", foreground="red")
                else:
                    widgets['status'].config(text=f"⏳ {line}", foreground="black")
            else:
                widgets['status'].config(text="Idle", foreground="gray")

            # Update last run time
            last_run = self.manager.get_last_run_time(name)
            if last_run != 'Never':
                widgets['last_run'].config(text=last_run, foreground="blue")
            else:
                widgets['last_run'].config(text=last_run, foreground="gray")

        # Update status bar if available
        if self.status_bar:
            if self.manager.is_running():
                self.status_bar.config(text="⏳ Backups in progress...")
            else:
                self.status_bar.config(text="✅ Ready")

        # Schedule next update
        self.root.after(1000, self._update_status)

    def _start_all(self):
        """Start all backups."""
        if self.manager.is_running():
            messagebox.showwarning("Already Running", "Backups are already in progress.")
            return

        dry_run = self.dry_run_var.get()
        self.manager.start_all(dry_run=dry_run)
        if self.status_bar:
            self.status_bar.config(text="🚀 Backups started...")

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

    def _toggle_auto_run(self):
        """Toggle auto-run timer."""
        # Save setting to config
        self._save_auto_run_setting()

        if self.auto_run_enabled.get():
            # Get interval from config
            app_settings = self.manager.config.get('app_settings', {})
            interval_min = app_settings.get('auto_run_interval_min', 5)

            logger.info(f"Auto-run enabled: Running every {interval_min} minutes")
            if self.status_bar:
                self.status_bar.config(text=f"⏰ Auto-run enabled: Every {interval_min} min")

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
            if self.status_bar:
                self.status_bar.config(text="Auto-run disabled")

    def _save_auto_run_setting(self):
        """Save auto-run setting to config."""
        from config_manager import save_config
        try:
            self.manager.config['app_settings']['auto_run_enabled'] = self.auto_run_enabled.get()
            save_config(self.manager.config)
        except Exception as e:
            logger.error(f"Failed to save auto-run setting: {e}")

    def _start_auto_run_cycle(self):
        """Start the regular auto-run cycle."""
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

    def reload(self):
        """Reload the backup list after configuration changes."""
        self._refresh_backup_list()
