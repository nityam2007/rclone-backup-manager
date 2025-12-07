# Backup Tab | Python
"""Backup operations tab with modern UI."""

import threading
import time
import tkinter as tk
from typing import Dict, Optional, Callable

from ..utils.constants import ttk, messagebox, HAS_TTK_BOOTSTRAP, COLORS, logger
from ..core.backup_manager import BackupManager
from .components import create_tooltip, ModernCard
from .theme import ICONS, get_status_color, get_font, SPACING


class BackupTab:
    """Modern backup operations tab."""

    def __init__(
        self,
        parent: ttk.Frame,
        manager: BackupManager,
        root: tk.Tk,
        on_minimize: Optional[Callable] = None
    ):
        self.parent = parent
        self.manager = manager
        self.root = root
        self.on_minimize = on_minimize
        self.backup_widgets: Dict[str, Dict] = {}
        self.status_bar: Optional[ttk.Label] = None
        self.auto_run_timer: Optional[str] = None

    def setup(self):
        """Initialize the backup tab UI."""
        self._create_header()
        self._create_stats_bar()
        self._create_backup_list()
        self._refresh_backup_list()
        self._start_status_updates()
        self._check_auto_run()

    def _create_header(self):
        """Create the header with action buttons."""
        header = ttk.Frame(self.parent)
        header.pack(fill=tk.X, padx=15, pady=15)
        
        # Title
        title_frame = ttk.Frame(header)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(
            title_frame,
            text=f"{ICONS['sync']} Backup Operations",
            font=get_font(14, 'bold')
        ).pack(side=tk.LEFT)
        
        # Action buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        if HAS_TTK_BOOTSTRAP:
            # Start All button
            start_btn = ttk.Button(
                btn_frame,
                text=f"{ICONS['play']} Start All",
                command=self._start_all,
                bootstyle="success",
                width=14
            )
            start_btn.pack(side=tk.LEFT, padx=5)
            create_tooltip(start_btn, "Start all configured backups")
            
            # Run Once button
            run_once_btn = ttk.Button(
                btn_frame,
                text=f"{ICONS['bolt']} Run Once",
                command=self._run_once,
                bootstyle="info",
                width=14
            )
            run_once_btn.pack(side=tk.LEFT, padx=5)
            create_tooltip(run_once_btn, "Run backups once with notification")
            
            # Separator
            ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
            # Minimize button
            minimize_btn = ttk.Button(
                btn_frame,
                text=f"{ICONS['minimize']} Minimize",
                command=self._minimize_app,
                bootstyle="secondary-outline",
                width=12
            )
            minimize_btn.pack(side=tk.LEFT, padx=5)
            create_tooltip(minimize_btn, "Minimize to system tray")
        else:
            ttk.Button(btn_frame, text="Start All", command=self._start_all).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Run Once", command=self._run_once).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Minimize", command=self._minimize_app).pack(side=tk.LEFT, padx=2)

    def _create_stats_bar(self):
        """Create a statistics bar."""
        stats_frame = ttk.Frame(self.parent)
        stats_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Stats will be dynamically updated
        self.stats_label = ttk.Label(
            stats_frame,
            text="",
            foreground=COLORS['muted']
        )
        self.stats_label.pack(side=tk.LEFT)
        
        self._update_stats()

    def _update_stats(self):
        """Update the statistics display."""
        stats = self.manager.get_statistics()
        total = stats.get('total_runs', 0)
        success = stats.get('successful_runs', 0)
        failed = stats.get('failed_runs', 0)
        
        if total > 0:
            success_rate = (success / total) * 100
            self.stats_label.config(
                text=f"{ICONS['info']} Total runs: {total} | Success: {success} | Failed: {failed} | Success rate: {success_rate:.0f}%"
            )
        else:
            self.stats_label.config(text=f"{ICONS['info']} No backup history yet")

    def _create_backup_list(self):
        """Create the scrollable backup list."""
        list_frame = ttk.Labelframe(self.parent, text=f"{ICONS['folder']} Backup Sets", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollable container
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.backup_items_frame = ttk.Frame(canvas)
        
        self.backup_items_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=self.backup_items_frame, anchor=tk.NW)
        
        # Make canvas expand to full width
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all('<Button-4>', on_mousewheel)
        canvas.bind_all('<Button-5>', on_mousewheel)
        canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _refresh_backup_list(self):
        """Refresh the backup list display."""
        # Clear existing
        for widget in self.backup_items_frame.winfo_children():
            widget.destroy()
        self.backup_widgets.clear()
        
        backup_sets = self.manager.get_backup_sets()
        
        if not backup_sets:
            empty_frame = ttk.Frame(self.backup_items_frame)
            empty_frame.pack(fill=tk.X, pady=40)
            
            ttk.Label(
                empty_frame,
                text=f"{ICONS['folder']} No backup sets configured",
                font=get_font(11),
                foreground=COLORS['muted']
            ).pack()
            
            ttk.Label(
                empty_frame,
                text="Go to Configuration tab to add backup sets",
                foreground=COLORS['muted']
            ).pack(pady=(5, 0))
            return
        
        for backup_set in backup_sets:
            self._create_backup_card(backup_set)

    def _create_backup_card(self, backup_set: Dict):
        """Create a card for a backup set."""
        name = backup_set.get('name', 'unnamed')
        local = backup_set.get('local', '')
        remote = backup_set.get('remote', '')
        
        # Card frame
        card = ttk.Labelframe(
            self.backup_items_frame,
            text=f"{ICONS['folder']} {name}",
            padding=15
        )
        card.pack(fill=tk.X, padx=5, pady=8)
        
        # Info grid
        info_frame = ttk.Frame(card)
        info_frame.pack(fill=tk.X)
        
        # Source row
        ttk.Label(
            info_frame,
            text=f"{ICONS['folder']} Source:",
            font=get_font(9, 'bold')
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, SPACING['md']))
        
        source_label = ttk.Label(info_frame, text=local, foreground=COLORS['primary'])
        source_label.grid(row=0, column=1, sticky=tk.W)
        
        # Destination row
        ttk.Label(
            info_frame,
            text=f"{ICONS['cloud']} Destination:",
            font=get_font(9, 'bold')
        ).grid(row=1, column=0, sticky=tk.W, padx=(0, SPACING['md']), pady=(SPACING['sm'], 0))
        
        dest_label = ttk.Label(info_frame, text=remote, foreground=COLORS['success'])
        dest_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        # Last run row
        ttk.Label(
            info_frame,
            text=f"{ICONS['clock']} Last Run:",
            font=get_font(9, 'bold')
        ).grid(row=2, column=0, sticky=tk.W, padx=(0, SPACING['md']), pady=(SPACING['sm'], 0))
        
        last_run = self.manager.get_last_run_time(name)
        last_run_label = ttk.Label(
            info_frame,
            text=last_run,
            foreground=COLORS['muted'] if last_run == 'Never' else COLORS['info']
        )
        last_run_label.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.Frame(card)
        progress_frame.pack(fill=tk.X, pady=(15, 5))
        
        if HAS_TTK_BOOTSTRAP:
            progress = ttk.Progressbar(
                progress_frame,
                orient=tk.HORIZONTAL,
                mode='determinate',
                bootstyle="success-striped"
            )
        else:
            progress = ttk.Progressbar(
                progress_frame,
                orient=tk.HORIZONTAL,
                mode='determinate'
            )
        progress.pack(fill=tk.X)
        
        # Status label
        status_label = ttk.Label(
            card,
            text=f"{ICONS['info']} Idle",
            foreground=COLORS['muted']
        )
        status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Store references
        self.backup_widgets[name] = {
            'progress': progress,
            'status': status_label,
            'last_run': last_run_label,
            'card': card
        }

    def _start_status_updates(self):
        """Start periodic status updates."""
        self._update_status()

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
                
                if rc is not None:
                    if rc == 0:
                        widgets['status'].config(
                            text=f"{ICONS['success']} {line}",
                            foreground=COLORS['success']
                        )
                    else:
                        widgets['status'].config(
                            text=f"{ICONS['error']} {line}",
                            foreground=COLORS['danger']
                        )
                else:
                    widgets['status'].config(
                        text=f"{ICONS['loading']} {line}",
                        foreground=COLORS['primary']
                    )
            else:
                widgets['status'].config(
                    text=f"{ICONS['info']} Idle",
                    foreground=COLORS['muted']
                )
            
            # Update last run time
            last_run = self.manager.get_last_run_time(name)
            widgets['last_run'].config(
                text=last_run,
                foreground=COLORS['muted'] if last_run == 'Never' else COLORS['info']
            )
        
        # Update main status bar
        if self.status_bar:
            if self.manager.is_running():
                running = self.manager.get_running_count()
                self.status_bar.config(text=f"{ICONS['loading']} {running} backup(s) in progress...")
            else:
                self.status_bar.config(text=f"{ICONS['success']} Ready")
        
        # Schedule next update
        self.root.after(1000, self._update_status)

    def _start_all(self):
        """Start all backups."""
        if self.manager.is_running():
            messagebox.showwarning("Already Running", "Backups are already in progress.")
            return
        
        app_settings = self.manager.get_app_settings()
        dry_run = app_settings.get('dry_run', False)
        
        self.manager.start_all(dry_run=dry_run)
        self._update_stats()
        
        if self.status_bar:
            self.status_bar.config(text=f"{ICONS['play']} Backups started...")

    def _run_once(self):
        """Run backups once with completion notification."""
        if self.manager.is_running():
            messagebox.showwarning("Already Running", "Backups are already in progress.")
            return
        
        app_settings = self.manager.get_app_settings()
        dry_run = app_settings.get('dry_run', False)
        
        self.manager.start_all(dry_run=dry_run)
        
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
            
            icon = ICONS['success'] if not fail else ICONS['warning']
            msg = f"Backup completed!\n\n{ICONS['success']} Successful: {len(ok)}\n{ICONS['error']} Failed: {len(fail)}"
            
            if fail:
                msg += f"\n\nFailed backups:\n" + "\n".join(f"  - {n}" for n in fail)
            
            self.root.after(0, lambda: messagebox.showinfo("Backup Complete", msg))
            self.root.after(0, self._update_stats)
        
        threading.Thread(target=monitor, daemon=True).start()

    def _minimize_app(self):
        """Minimize to system tray."""
        if self.on_minimize:
            self.on_minimize()
        else:
            self.root.iconify()

    def _check_auto_run(self):
        """Check and start auto-run if enabled."""
        app_settings = self.manager.get_app_settings()
        if app_settings.get('auto_run_enabled', False):
            self._start_auto_run()

    def _start_auto_run(self):
        """Start the auto-run cycle."""
        app_settings = self.manager.get_app_settings()
        interval_min = app_settings.get('auto_run_interval_min', 5)
        
        logger.info(f"Auto-run enabled: Every {interval_min} minutes")
        
        def run_cycle():
            if not self.manager.is_running():
                logger.info("Auto-run: Starting backup")
                self.manager.start_all(dry_run=False)
            
            # Schedule next
            self.auto_run_timer = self.root.after(
                interval_min * 60 * 1000,
                run_cycle
            )
        
        run_cycle()

    def reload(self):
        """Reload the backup list."""
        self._refresh_backup_list()
        self._update_stats()
