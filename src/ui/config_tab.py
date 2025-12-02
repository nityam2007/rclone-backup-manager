# Configuration Tab | Python
"""Configuration editor tab with modern UI."""

import tkinter as tk
from typing import Callable, Optional

from ..utils.constants import ttk, messagebox, filedialog, CFG_FILE, HAS_TTK_BOOTSTRAP, COLORS
from ..core.backup_manager import BackupManager
from ..core.config_manager import save_config
from ..core.rclone_runner import list_remotes
from .components import create_tooltip
from .theme import ICONS


class ConfigTab:
    """Modern configuration editor tab."""

    def __init__(self, parent: ttk.Frame, manager: BackupManager, on_reload: Callable):
        self.parent = parent
        self.manager = manager
        self.on_reload = on_reload
        
        # Settings variables
        self.transfers_var = tk.StringVar(value="8")
        self.checkers_var = tk.StringVar(value="8")
        self.retries_var = tk.StringVar(value="3")
        self.start_minimized_var = tk.BooleanVar(value=False)
        self.dry_run_var = tk.BooleanVar(value=False)
        self.auto_run_var = tk.BooleanVar(value=False)
        self.auto_run_interval_var = tk.StringVar(value="5")
        
        self.config_items_frame: Optional[ttk.Frame] = None

    def setup(self):
        """Initialize the configuration tab UI."""
        self._create_header()
        self._create_settings_section()
        self._create_backup_list()
        self._load_config_to_form()

    def _create_header(self):
        """Create the header with action buttons."""
        header = ttk.Frame(self.parent)
        header.pack(fill=tk.X, padx=15, pady=15)
        
        # Title
        title_frame = ttk.Frame(header)
        title_frame.pack(side=tk.LEFT)
        
        ttk.Label(
            title_frame,
            text=f"{ICONS['settings']} Configuration",
            font=('Segoe UI', 14, 'bold')
        ).pack(side=tk.LEFT)
        
        # Config file indicator
        ttk.Label(
            title_frame,
            text=f"  |  {ICONS['file']} {CFG_FILE.name}",
            foreground=COLORS['muted']
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Action buttons
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side=tk.RIGHT)
        
        if HAS_TTK_BOOTSTRAP:
            add_btn = ttk.Button(
                btn_frame,
                text=f"{ICONS['add']} Add Backup",
                command=self._add_backup_dialog,
                bootstyle="success",
                width=14
            )
            add_btn.pack(side=tk.LEFT, padx=5)
            create_tooltip(add_btn, "Add a new backup configuration")
            
            save_btn = ttk.Button(
                btn_frame,
                text=f"{ICONS['save']} Save Changes",
                command=self._save_config_from_form,
                bootstyle="primary",
                width=14
            )
            save_btn.pack(side=tk.LEFT, padx=5)
            create_tooltip(save_btn, "Save all configuration changes")
        else:
            ttk.Button(btn_frame, text="Add Backup", command=self._add_backup_dialog).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Save Changes", command=self._save_config_from_form).pack(side=tk.LEFT, padx=2)

    def _create_settings_section(self):
        """Create the settings section."""
        settings_frame = ttk.Labelframe(
            self.parent,
            text=f"{ICONS['settings']} General Settings",
            padding=15
        )
        settings_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Grid layout
        grid = ttk.Frame(settings_frame)
        grid.pack(fill=tk.X)
        
        # Row 1: Performance settings
        row = 0
        
        ttk.Label(grid, text="Transfers:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        transfers_entry = ttk.Entry(grid, textvariable=self.transfers_var, width=8)
        transfers_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        create_tooltip(transfers_entry, "Number of parallel file transfers")
        
        ttk.Label(grid, text="Checkers:").grid(row=row, column=2, sticky=tk.W, padx=(20, 5), pady=5)
        checkers_entry = ttk.Entry(grid, textvariable=self.checkers_var, width=8)
        checkers_entry.grid(row=row, column=3, sticky=tk.W, padx=5, pady=5)
        create_tooltip(checkers_entry, "Number of parallel file checkers")
        
        ttk.Label(grid, text="Retries:").grid(row=row, column=4, sticky=tk.W, padx=(20, 5), pady=5)
        retries_entry = ttk.Entry(grid, textvariable=self.retries_var, width=8)
        retries_entry.grid(row=row, column=5, sticky=tk.W, padx=5, pady=5)
        create_tooltip(retries_entry, "Number of retries on failure")
        
        # Row 2: Toggles
        row = 1
        toggle_frame = ttk.Frame(grid)
        toggle_frame.grid(row=row, column=0, columnspan=6, sticky=tk.W, pady=(10, 0))
        
        if HAS_TTK_BOOTSTRAP:
            ttk.Checkbutton(
                toggle_frame,
                text="Start Minimized",
                variable=self.start_minimized_var,
                bootstyle="round-toggle"
            ).pack(side=tk.LEFT, padx=(0, 20))
            
            ttk.Checkbutton(
                toggle_frame,
                text="Dry Run Mode",
                variable=self.dry_run_var,
                bootstyle="warning-round-toggle"
            ).pack(side=tk.LEFT, padx=(0, 20))
            
            ttk.Checkbutton(
                toggle_frame,
                text="Auto-Run",
                variable=self.auto_run_var,
                bootstyle="success-round-toggle"
            ).pack(side=tk.LEFT, padx=(0, 10))
        else:
            ttk.Checkbutton(toggle_frame, text="Start Minimized", variable=self.start_minimized_var).pack(side=tk.LEFT, padx=(0, 15))
            ttk.Checkbutton(toggle_frame, text="Dry Run", variable=self.dry_run_var).pack(side=tk.LEFT, padx=(0, 15))
            ttk.Checkbutton(toggle_frame, text="Auto-Run", variable=self.auto_run_var).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(toggle_frame, text="every").pack(side=tk.LEFT, padx=(0, 5))
        interval_entry = ttk.Entry(toggle_frame, textvariable=self.auto_run_interval_var, width=5)
        interval_entry.pack(side=tk.LEFT)
        ttk.Label(toggle_frame, text="min").pack(side=tk.LEFT, padx=(5, 0))
        create_tooltip(interval_entry, "Auto-run interval in minutes")

    def _create_backup_list(self):
        """Create the backup sets list."""
        list_frame = ttk.Labelframe(
            self.parent,
            text=f"{ICONS['folder']} Configured Backups",
            padding=10
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollable container
        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.config_items_frame = ttk.Frame(canvas)
        
        self.config_items_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=self.config_items_frame, anchor=tk.NW)
        
        def configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', configure_canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel
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

    def _load_config_to_form(self):
        """Load configuration into the form."""
        config = self.manager.config
        settings = config.get('settings', {})
        app_settings = config.get('app_settings', {})
        
        # Update settings
        self.transfers_var.set(str(settings.get('transfers', 8)))
        self.checkers_var.set(str(settings.get('checkers', 8)))
        self.retries_var.set(str(settings.get('retries', 3)))
        
        self.start_minimized_var.set(app_settings.get('start_minimized', False))
        self.dry_run_var.set(app_settings.get('dry_run', False))
        self.auto_run_var.set(app_settings.get('auto_run_enabled', False))
        self.auto_run_interval_var.set(str(app_settings.get('auto_run_interval_min', 5)))
        
        # Clear and rebuild backup list
        for widget in self.config_items_frame.winfo_children():
            widget.destroy()
        
        backup_sets = config.get('backup_sets', [])
        
        if not backup_sets:
            empty_frame = ttk.Frame(self.config_items_frame)
            empty_frame.pack(fill=tk.X, pady=30)
            
            ttk.Label(
                empty_frame,
                text=f"{ICONS['add']} No backups configured",
                font=('Segoe UI', 11),
                foreground=COLORS['muted']
            ).pack()
            
            ttk.Label(
                empty_frame,
                text="Click 'Add Backup' to create your first backup set",
                foreground=COLORS['muted']
            ).pack(pady=(5, 0))
            return
        
        for backup_set in backup_sets:
            self._add_backup_item_to_form(backup_set)

    def _add_backup_item_to_form(self, backup_set: dict):
        """Add a backup item to the form."""
        name = backup_set.get('name', '')
        local = backup_set.get('local', '')
        remote = backup_set.get('remote', '')
        
        # Card frame
        card = ttk.Labelframe(
            self.config_items_frame,
            text=f"{ICONS['folder']} {name or 'New Backup'}",
            padding=15
        )
        card.pack(fill=tk.X, padx=5, pady=8)
        
        # Content layout
        content = ttk.Frame(card)
        content.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        # Name field
        row = ttk.Frame(content)
        row.pack(fill=tk.X, pady=3)
        
        ttk.Label(row, text="Name:", width=10).pack(side=tk.LEFT)
        name_var = tk.StringVar(value=name)
        name_entry = ttk.Entry(row, textvariable=name_var, width=40)
        name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Local path field
        row = ttk.Frame(content)
        row.pack(fill=tk.X, pady=3)
        
        ttk.Label(row, text="Local:", width=10).pack(side=tk.LEFT)
        local_var = tk.StringVar(value=local)
        local_entry = ttk.Entry(row, textvariable=local_var)
        local_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        if HAS_TTK_BOOTSTRAP:
            browse_btn = ttk.Button(
                row,
                text=f"{ICONS['folder_open']}",
                command=lambda: self._browse_folder(local_var),
                bootstyle="secondary-outline",
                width=4
            )
        else:
            browse_btn = ttk.Button(
                row,
                text="...",
                command=lambda: self._browse_folder(local_var),
                width=4
            )
        browse_btn.pack(side=tk.LEFT)
        create_tooltip(browse_btn, "Browse for folder")
        
        # Remote path field
        row = ttk.Frame(content)
        row.pack(fill=tk.X, pady=3)
        
        ttk.Label(row, text="Remote:", width=10).pack(side=tk.LEFT)
        remote_var = tk.StringVar(value=remote)
        remote_entry = ttk.Entry(row, textvariable=remote_var)
        remote_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        create_tooltip(remote_entry, "Format: remotename:path/to/folder")
        
        # Delete button
        btn_frame = ttk.Frame(card)
        btn_frame.pack(side=tk.RIGHT, padx=(15, 0))
        
        if HAS_TTK_BOOTSTRAP:
            del_btn = ttk.Button(
                btn_frame,
                text=f"{ICONS['delete']}",
                command=lambda: self._delete_backup_item(card),
                bootstyle="danger-outline",
                width=4
            )
        else:
            del_btn = ttk.Button(
                btn_frame,
                text="X",
                command=lambda: self._delete_backup_item(card),
                width=4
            )
        del_btn.pack()
        create_tooltip(del_btn, "Delete this backup")
        
        # Store references
        card.name_var = name_var
        card.local_var = local_var
        card.remote_var = remote_var

    def _browse_folder(self, var: tk.StringVar):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Folder",
            mustexist=True
        )
        if folder:
            var.set(folder)

    def _delete_backup_item(self, frame: ttk.Labelframe):
        """Delete a backup item."""
        if messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this backup configuration?",
            icon='warning'
        ):
            frame.destroy()

    def _add_backup_dialog(self):
        """Show dialog to add new backup."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Backup")
        dialog.geometry("550x280")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center on parent
        dialog.update_idletasks()
        x = self.parent.winfo_toplevel().winfo_x() + 100
        y = self.parent.winfo_toplevel().winfo_y() + 100
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding=25)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(
            frame,
            text=f"{ICONS['add']} New Backup Configuration",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Form fields
        form = ttk.Frame(frame)
        form.pack(fill=tk.X)
        
        # Name
        row = ttk.Frame(form)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Name:", width=12).pack(side=tk.LEFT)
        name_var = tk.StringVar()
        ttk.Entry(row, textvariable=name_var, width=45).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Local folder
        row = ttk.Frame(form)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Local Folder:", width=12).pack(side=tk.LEFT)
        local_var = tk.StringVar()
        ttk.Entry(row, textvariable=local_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(row, text="Browse", command=lambda: self._browse_folder(local_var), width=8).pack(side=tk.LEFT)
        
        # Remote path
        row = ttk.Frame(form)
        row.pack(fill=tk.X, pady=5)
        ttk.Label(row, text="Remote Path:", width=12).pack(side=tk.LEFT)
        remote_var = tk.StringVar()
        ttk.Entry(row, textvariable=remote_var, width=45).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Help text
        ttk.Label(
            form,
            text="Example remote: gdrive:Backups/MyFolder or onedrive:Documents",
            foreground=COLORS['muted'],
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(25, 0))
        
        def add_backup():
            if not name_var.get().strip():
                messagebox.showwarning("Missing Name", "Please enter a name for the backup.")
                return
            if not local_var.get().strip():
                messagebox.showwarning("Missing Path", "Please select a local folder.")
                return
            if not remote_var.get().strip():
                messagebox.showwarning("Missing Remote", "Please enter a remote path.")
                return
            if ':' not in remote_var.get():
                messagebox.showwarning("Invalid Remote", "Remote must include rclone remote name (e.g., gdrive:path)")
                return
            
            self._add_backup_item_to_form({
                'name': name_var.get().strip(),
                'local': local_var.get().strip(),
                'remote': remote_var.get().strip()
            })
            dialog.destroy()
        
        if HAS_TTK_BOOTSTRAP:
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, bootstyle="secondary", width=12).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(btn_frame, text=f"{ICONS['add']} Add", command=add_backup, bootstyle="success", width=12).pack(side=tk.RIGHT)
        else:
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=12).pack(side=tk.RIGHT, padx=(10, 0))
            ttk.Button(btn_frame, text="Add", command=add_backup, width=12).pack(side=tk.RIGHT)
        
        dialog.bind('<Escape>', lambda e: dialog.destroy())
        dialog.bind('<Return>', lambda e: add_backup())

    def _save_config_from_form(self):
        """Save configuration from form values."""
        try:
            # Validate numeric inputs
            transfers = int(self.transfers_var.get())
            checkers = int(self.checkers_var.get())
            retries = int(self.retries_var.get())
            interval = int(self.auto_run_interval_var.get())
            
            if transfers < 1 or checkers < 1 or retries < 0 or interval < 1:
                raise ValueError("Invalid numeric value")
            
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid numbers for Transfers, Checkers, Retries, and Interval."
            )
            return
        
        # Build settings
        settings = {
            'transfers': transfers,
            'checkers': checkers,
            'retries': retries,
            'retries_sleep': '10s'
        }
        
        # Build app settings
        app_settings = self.manager.config.get('app_settings', {})
        app_settings.update({
            'start_minimized': self.start_minimized_var.get(),
            'dry_run': self.dry_run_var.get(),
            'auto_run_enabled': self.auto_run_var.get(),
            'auto_run_interval_min': interval
        })
        
        # Collect backup sets
        backup_sets = []
        for widget in self.config_items_frame.winfo_children():
            if hasattr(widget, 'name_var'):
                name = widget.name_var.get().strip()
                local = widget.local_var.get().strip()
                remote = widget.remote_var.get().strip()
                
                if name and local and remote:
                    backup_sets.append({
                        'name': name,
                        'local': local,
                        'remote': remote
                    })
        
        # Build config
        config = {
            'backup_sets': backup_sets,
            'settings': settings,
            'app_settings': app_settings
        }
        
        # Save
        if save_config(config):
            self.manager.config = config
            self.on_reload()
            messagebox.showinfo(
                "Saved",
                f"{ICONS['success']} Configuration saved successfully!\n\n{len(backup_sets)} backup(s) configured."
            )
        else:
            messagebox.showerror("Error", "Failed to save configuration.")

    def reload(self):
        """Reload the configuration form."""
        self._load_config_to_form()
