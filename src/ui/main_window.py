# Main Window | Python
"""Main application window with tabbed interface."""

import os
import subprocess
import sys
import tkinter as tk
from typing import Optional

from ..utils.constants import (
    APP_NAME, VERSION, HAS_TRAY, IS_WINDOWS,
    CFG_FILE, HAS_TTK_BOOTSTRAP, DEFAULT_THEME, DARK_THEME,
    ttk, messagebox, logger
)
from ..core.backup_manager import BackupManager
from ..core.config_manager import save_config
from ..utils.tray_manager import TrayManager
from .components import (
    create_menu_bar, create_status_bar,
    show_about_dialog, show_documentation_dialog, show_shortcuts_dialog
)
from .backup_tab import BackupTab
from .config_tab import ConfigTab
from .logs_tab import LogsTab
from .theme import ThemeManager, ICONS

if HAS_TRAY:
    from PIL import Image, ImageDraw, ImageTk


class MainWindow:
    """Main application window."""

    def __init__(self, manager: BackupManager):
        self.manager = manager
        
        # Load theme setting
        app_settings = self.manager.config.get('app_settings', {})
        self.current_theme = app_settings.get('theme', DEFAULT_THEME)
        
        # Create root window
        if HAS_TTK_BOOTSTRAP:
            import ttkbootstrap as ttkb
            self.root = ttkb.Window(themename=self.current_theme)
        else:
            self.root = tk.Tk()
        
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        
        self._set_window_icon()
        
        # Tray management
        self.tray_manager: Optional[TrayManager] = None
        self.is_minimized_to_tray = False
        self.minimize_to_tray_enabled = tk.BooleanVar(
            value=app_settings.get('minimize_to_tray', True)
        )
        
        # UI components
        self.backup_tab: Optional[BackupTab] = None
        self.config_tab: Optional[ConfigTab] = None
        self.logs_tab: Optional[LogsTab] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.status_bar: Optional[ttk.Label] = None
        self.backup_count_label: Optional[ttk.Label] = None
        
        self._setup_ui()
        self._setup_tray()
        
        # Check start minimized
        if app_settings.get('start_minimized', False) and HAS_TRAY:
            self.root.after(100, self._start_minimized)
        
        # Bindings
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Unmap>", self._on_minimize)
        self.root.bind('<F5>', lambda e: self._reload_config())
        self.root.bind('<Control-q>', lambda e: self._on_close())
        self.root.bind('<Control-Q>', lambda e: self._on_close())

    def _set_window_icon(self):
        """Set the window icon."""
        try:
            if HAS_TRAY:
                size = 32
                img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.ellipse((2, 2, size-2, size-2), fill=(13, 110, 253))
                draw.ellipse((4, 4, size-4, size-4), fill=(30, 125, 255))
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                self._icon_photo = photo  # Keep reference
        except Exception:
            pass

    def _setup_ui(self):
        """Setup the main UI."""
        # Menu bar
        menu_callbacks = {
            'reload_config': self._reload_config,
            'view_config_file': self._view_config_file,
            'on_close': self._on_close,
            'show_documentation': lambda: show_documentation_dialog(self.root),
            'show_shortcuts': lambda: show_shortcuts_dialog(self.root),
            'show_about': lambda: show_about_dialog(self.root),
            'toggle_tray': self._toggle_tray_enabled,
            'toggle_dark_mode': self._toggle_dark_mode
        }
        menubar = create_menu_bar(self.root, menu_callbacks)
        self.root.config(menu=menubar)
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook (tabs)
        if HAS_TTK_BOOTSTRAP:
            self.notebook = ttk.Notebook(main_frame, bootstyle="default")
        else:
            self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._setup_tabs()
        
        # Status bar
        self.status_bar, self.backup_count_label = create_status_bar(self.root, "Ready")
        self._update_backup_count()

    def _setup_tabs(self):
        """Setup all tabs."""
        # Backup Tab
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text=f" {ICONS['sync']} Backups ")
        self.backup_tab = BackupTab(
            backup_frame,
            self.manager,
            self.root,
            on_minimize=self._minimize_to_tray
        )
        self.backup_tab.status_bar = self.status_bar
        self.backup_tab.setup()
        
        # Configuration Tab
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text=f" {ICONS['settings']} Configuration ")
        self.config_tab = ConfigTab(config_frame, self.manager, self._reload_all_tabs)
        self.config_tab.setup()
        
        # Logs Tab
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text=f" {ICONS['file']} Logs ")
        self.logs_tab = LogsTab(logs_frame, self.manager, self.root)
        self.logs_tab.setup()

    def _setup_tray(self):
        """Setup system tray icon."""
        if not HAS_TRAY:
            return
        
        from ..utils.tray_manager import TrayManager
        
        self.tray_manager = TrayManager(
            on_show=self._restore_from_tray,
            on_start=self._start_backups_from_tray,
            on_quit=self._quit_app
        )
        self.tray_manager.create_icon()

    def _update_backup_count(self):
        """Update the backup count in status bar."""
        count = len(self.manager.get_backup_sets())
        self.backup_count_label.config(text=f"{ICONS['folder']} {count} backup(s)")

    def _reload_config(self):
        """Reload configuration from file."""
        self.manager.reload_config()
        self._reload_all_tabs()
        messagebox.showinfo("Reloaded", f"{ICONS['success']} Configuration reloaded successfully.")

    def _reload_all_tabs(self):
        """Reload all tabs after configuration changes."""
        if self.backup_tab:
            self.backup_tab.reload()
        if self.config_tab:
            self.config_tab.reload()
        if self.logs_tab:
            self.logs_tab.reload()
        
        self._update_backup_count()

    def _view_config_file(self):
        """Open config file in default editor."""
        if not CFG_FILE.exists():
            messagebox.showinfo("No Config", "Configuration file doesn't exist yet.")
            return
        
        try:
            if IS_WINDOWS:
                os.startfile(CFG_FILE)
            else:
                subprocess.Popen(['xdg-open', str(CFG_FILE)])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open config file:\n{e}")

    def _on_minimize(self, event):
        """Handle window minimize event."""
        if event.widget != self.root:
            return
        
        if self.root.state() == 'iconic':
            self._minimize_to_tray()
        else:
            self.root.after(100, self._check_minimize_state)

    def _check_minimize_state(self):
        """Check if window was minimized."""
        if self.root.state() == 'iconic':
            self._minimize_to_tray()

    def _minimize_to_tray(self):
        """Minimize to system tray."""
        if not self.minimize_to_tray_enabled.get():
            return
        
        if HAS_TRAY and self.tray_manager and not self.is_minimized_to_tray:
            self.root.withdraw()
            self.is_minimized_to_tray = True
            self.tray_manager.run()

    def _start_minimized(self):
        """Start application minimized to tray."""
        if HAS_TRAY and self.tray_manager:
            self.root.withdraw()
            self.is_minimized_to_tray = True
            self.tray_manager.run()

    def _restore_from_tray(self, icon=None, item=None):
        """Restore window from tray."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_minimized_to_tray = False

    def _start_backups_from_tray(self, icon=None, item=None):
        """Start backups from tray menu."""
        if self.backup_tab:
            self.backup_tab._start_all()

    def _on_close(self):
        """Handle window close event."""
        if self.manager.is_running():
            if not messagebox.askokcancel(
                "Backups Running",
                "Backups are currently running.\nAre you sure you want to exit?"
            ):
                return
        
        self._quit_app()

    def _quit_app(self, icon=None, item=None):
        """Quit the application."""
        if self.tray_manager:
            self.tray_manager.stop()
        
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        
        sys.exit(0)

    def _toggle_tray_enabled(self):
        """Toggle minimize-to-tray setting."""
        current = self.minimize_to_tray_enabled.get()
        self.minimize_to_tray_enabled.set(not current)
        
        try:
            self.manager.config['app_settings']['minimize_to_tray'] = self.minimize_to_tray_enabled.get()
            save_config(self.manager.config)
            
            status = "enabled" if self.minimize_to_tray_enabled.get() else "disabled"
            messagebox.showinfo("Setting Changed", f"Minimize to tray is now {status}.")
        except Exception as e:
            logger.error(f"Failed to save tray setting: {e}")
            messagebox.showerror("Error", "Could not save setting.")

    def _toggle_dark_mode(self):
        """Toggle between light and dark themes."""
        if not HAS_TTK_BOOTSTRAP:
            messagebox.showinfo("Not Available", "Theme switching requires ttkbootstrap.")
            return
        
        new_theme = DARK_THEME if self.current_theme == DEFAULT_THEME else DEFAULT_THEME
        
        try:
            self.root.style.theme_use(new_theme)
            self.current_theme = new_theme
            
            self.manager.config['app_settings']['theme'] = new_theme
            save_config(self.manager.config)
            
            logger.info(f"Theme switched to: {new_theme}")
        except Exception as e:
            logger.error(f"Failed to switch theme: {e}")
            messagebox.showerror("Error", "Could not switch theme.")

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
