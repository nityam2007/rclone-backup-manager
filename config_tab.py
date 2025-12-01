#!/usr/bin/env python3
"""Configuration editor tab UI and logic."""

from typing import Callable

from constants import ttk, messagebox, filedialog, CFG_FILE, HAS_TTK_BOOTSTRAP
from backup_manager import BackupManager
from config_manager import save_config
from ui_components import create_tooltip


class ConfigTab:
    """Configuration editor tab component."""

    def __init__(self, parent, manager: BackupManager, on_reload: Callable):
        self.parent = parent
        self.manager = manager
        self.on_reload = on_reload
        
        import tkinter as tk
        self.transfers_var = tk.StringVar(value="8")
        self.checkers_var = tk.StringVar(value="8")
        self.retries_var = tk.StringVar(value="3")
        self.start_minimized_var = tk.BooleanVar(value=False)

    def setup(self):
        """Setup the configuration tab UI."""
        self._create_toolbar()
        self._create_settings_section()
        self._create_backup_list()
        self._load_config_to_form()

    def _create_toolbar(self):
        """Create the toolbar."""
        import tkinter as tk
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill='x', padx=10, pady=10)

        if HAS_TTK_BOOTSTRAP:
            add_btn = ttk.Button(
                toolbar,
                text="➕ Add New Backup",
                command=self._add_backup_dialog,
                bootstyle="success",
                width=18
            )
            add_btn.pack(side='left', padx=5)
            create_tooltip(add_btn, "Create a new backup configuration")

            save_btn = ttk.Button(
                toolbar,
                text="💾 Save All Changes",
                command=self._save_config_from_form,
                bootstyle="primary",
                width=18
            )
            save_btn.pack(side='left', padx=5)
            create_tooltip(save_btn, "Save all configuration changes to file")
        else:
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
            text=f"📝 Config: {CFG_FILE.name}"
        ).pack(side='right', padx=5)

    def _create_settings_section(self):
        """Create the settings fields section."""
        import tkinter as tk
        settings_frame = ttk.Labelframe(self.parent, text="⚙️ Settings", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)

        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill='x')

        ttk.Label(settings_grid, text="Transfers:").grid(row=0, column=0, sticky='w', padx=5)
        ttk.Entry(settings_grid, textvariable=self.transfers_var, width=10).grid(row=0, column=1, sticky='w')

        ttk.Label(settings_grid, text="Checkers:").grid(row=0, column=2, sticky='w', padx=(20, 5))
        ttk.Entry(settings_grid, textvariable=self.checkers_var, width=10).grid(row=0, column=3, sticky='w')

        ttk.Label(settings_grid, text="Retries:").grid(row=0, column=4, sticky='w', padx=(20, 5))
        ttk.Entry(settings_grid, textvariable=self.retries_var, width=10).grid(row=0, column=5, sticky='w')

        ttk.Checkbutton(
            settings_grid,
            text="Start Minimized",
            variable=self.start_minimized_var,
            bootstyle="round-toggle" if HAS_TTK_BOOTSTRAP else ""
        ).grid(row=0, column=6, sticky='w', padx=(20, 5))

    def _create_backup_list(self):
        """Create the backup sets list editor."""
        import tkinter as tk
        list_frame = ttk.Labelframe(self.parent, text="📋 Configured Backups", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        self.config_items_frame = ttk.Frame(canvas)

        self.config_items_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.config_items_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def _load_config_to_form(self):
        """Load config into the form-based UI."""
        import tkinter as tk
        config = self.manager.config
        settings = config.get('settings', {})

        self.transfers_var.set(str(settings.get('transfers', 8)))
        self.checkers_var.set(str(settings.get('checkers', 8)))
        self.retries_var.set(str(settings.get('retries', 3)))

        app_settings = config.get('app_settings', {})
        self.start_minimized_var.set(app_settings.get('start_minimized', False))

        for widget in self.config_items_frame.winfo_children():
            widget.destroy()

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
        import tkinter as tk
        name = backup_set.get('name', '')
        local = backup_set.get('local', '')
        remote = backup_set.get('remote', '')

        item_frame = ttk.Labelframe(self.config_items_frame, text=f"📁 {name}", padding=10)
        item_frame.pack(fill='x', padx=5, pady=5)

        fields_frame = ttk.Frame(item_frame)
        fields_frame.pack(fill='x', side='left', expand=True)

        ttk.Label(fields_frame, text="Name:").grid(row=0, column=0, sticky='w', padx=5)
        name_var = tk.StringVar(value=name)
        ttk.Entry(fields_frame, textvariable=name_var, width=30).grid(row=0, column=1, sticky='ew', padx=5)

        ttk.Label(fields_frame, text="Local:").grid(row=1, column=0, sticky='w', padx=5)
        local_var = tk.StringVar(value=local)
        local_entry = ttk.Entry(fields_frame, textvariable=local_var, width=50)
        local_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        browse_btn = ttk.Button(
            fields_frame,
            text="Browse",
            command=lambda: self._browse_folder(local_var),
            width=8
        )
        browse_btn.grid(row=1, column=2, padx=5)
        create_tooltip(browse_btn, "Select local folder")

        ttk.Label(fields_frame, text="Remote:").grid(row=2, column=0, sticky='w', padx=5)
        remote_var = tk.StringVar(value=remote)
        ttk.Entry(fields_frame, textvariable=remote_var, width=50).grid(row=2, column=1, sticky='ew', padx=5)

        fields_frame.columnconfigure(1, weight=1)

        if HAS_TTK_BOOTSTRAP:
            del_btn = ttk.Button(
                item_frame,
                text="🗑️ Delete",
                command=lambda: self._delete_backup_item(item_frame),
                bootstyle="danger",
                width=10
            )
            del_btn.pack(side='right', padx=5)
            create_tooltip(del_btn, "Remove this backup configuration")
        else:
            ttk.Button(
                item_frame,
                text="Delete",
                command=lambda: self._delete_backup_item(item_frame),
                width=8
            ).pack(side='right', padx=5)

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
        import tkinter as tk
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Backup")
        dialog.geometry("500x200")
        dialog.transient(self.parent)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky='w', pady=5)
        name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=name_var, width=40).grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(frame, text="Local Folder:").grid(row=1, column=0, sticky='w', pady=5)
        local_var = tk.StringVar()
        ttk.Entry(frame, textvariable=local_var, width=40).grid(row=1, column=1, sticky='ew', pady=5)
        ttk.Button(
            frame,
            text="Browse",
            command=lambda: self._browse_folder(local_var)
        ).grid(row=1, column=2, padx=5)

        ttk.Label(frame, text="Remote Path:").grid(row=2, column=0, sticky='w', pady=5)
        remote_var = tk.StringVar()
        ttk.Entry(frame, textvariable=remote_var, width=40).grid(row=2, column=1, sticky='ew', pady=5)

        ttk.Label(
            frame,
            text="Example: myremote:bucket/path",
            foreground="gray",
            font=('TkDefaultFont', 8)
        ).grid(row=3, column=1, sticky='w')

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

        if HAS_TTK_BOOTSTRAP:
            ttk.Button(btn_frame, text="Add", command=add_backup, bootstyle="success").pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, bootstyle="secondary").pack(side='left', padx=5)
        else:
            ttk.Button(btn_frame, text="Add", command=add_backup).pack(side='left', padx=5)
            ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)

    def _save_config_from_form(self):
        """Save configuration from form fields."""
        try:
            settings = {
                'transfers': int(self.transfers_var.get()),
                'checkers': int(self.checkers_var.get()),
                'retries': int(self.retries_var.get()),
                'retries_sleep': '10s'
            }

            backup_sets = []
            for item_frame in self.config_items_frame.winfo_children():
                if hasattr(item_frame, 'name_var'):
                    backup_sets.append({
                        'name': item_frame.name_var.get(),
                        'local': item_frame.local_var.get(),
                        'remote': item_frame.remote_var.get()
                    })

            app_settings = self.manager.config.get('app_settings', {
                'minimize_to_tray': True,
                'auto_run_enabled': False,
                'auto_run_interval_min': 5,
                'theme': 'cosmo'
            })
            app_settings['start_minimized'] = self.start_minimized_var.get()

            config = {
                'backup_sets': backup_sets,
                'settings': settings,
                'app_settings': app_settings
            }

            if save_config(config):
                self.manager.config = config
                self.on_reload()
                messagebox.showinfo("Saved", "Configuration saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save configuration.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your settings values:\n{e}")

    def reload(self):
        """Reload the configuration form."""
        self._load_config_to_form()
