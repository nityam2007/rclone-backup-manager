#!/usr/bin/env python3
"""Main application window and tab management."""

import os
import subprocess
import tkinter as tk

from constants import (
    APP_NAME, VERSION, HAS_TRAY, IS_WINDOWS, CFG_FILE,
    HAS_TTK_BOOTSTRAP, DEFAULT_THEME, DARK_THEME, ttk, messagebox, logger
)
from backup_manager import BackupManager
from tray_manager import TrayManager
from ui_components import (
    create_menu_bar, create_status_bar,
    show_about_dialog, show_documentation_dialog, show_shortcuts_dialog
)
from backup_tab import BackupTab
from config_tab import ConfigTab
from logs_tab import LogsTab

if HAS_TRAY:
    from PIL import Image, ImageDraw, ImageTk


class MainWindow:
    """Main application window with tabbed interface."""

    def __init__(self, manager: BackupManager):
        self.manager = manager
        
        # Load settings
        app_settings = self.manager.config.get('app_settings', {})
        self.current_theme = app_settings.get('theme', DEFAULT_THEME)

        # Initialize Window
        if HAS_TTK_BOOTSTRAP:
            self.root = ttk.Window(themename=self.current_theme)
        else:
            self.root = tk.Tk()

        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1000x650")
        self.root.minsize(800, 500)

        self._set_window_icon()

        # Tray setup
        self.tray_manager = None
        self.is_minimized_to_tray = False
        self.minimize_to_tray_enabled = tk.BooleanVar(
            value=app_settings.get('minimize_to_tray', True)
        )

        # UI Components
        self.backup_tab = None
        self.config_tab = None
        self.logs_tab = None
        self.notebook = None
        self.status_bar = None
        self.backup_count_label = None

        self._setup_ui()
        self._setup_tray()

        # Event Bindings
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Unmap>", self._on_minimize)
        self.root.bind('<F5>', lambda e: self._reload_config())
        self.root.bind('<Control-q>', lambda e: self._on_close())

    def _set_window_icon(self):
        """Set the window icon."""
        try:
            if HAS_TRAY:
                icon_img = Image.new('RGB', (32, 32), color=(0, 120, 215))
                draw = ImageDraw.Draw(icon_img)
                draw.rectangle((4, 4, 28, 28), fill=(255, 255, 255))
                draw.text((8, 8), "R", fill=(0, 120, 215))
                photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, photo)
        except Exception:
            pass

    def _setup_ui(self):
        """Setup the main UI components."""
        import tkinter as tk
        
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
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self._setup_tabs()

        # Status bar
        self.status_bar, self.backup_count_label = create_status_bar(self.root, "Ready")
        
        # Update backup count
        backup_count = len(self.manager.get_backup_sets())
        self.backup_count_label.config(text=f"{backup_count} backup(s) configured")

    def _setup_tabs(self):
        """Setup all tabs."""
        # Tab 1: Backup Operations
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="Backups")
        self.backup_tab = BackupTab(backup_frame, self.manager, self.root)
        self.backup_tab.status_bar = self.status_bar
        self.backup_tab.setup()

        # Tab 2: Configuration Editor
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        self.config_tab = ConfigTab(config_frame, self.manager, self._reload_all_tabs)
        self.config_tab.setup()

        # Tab 3: Logs
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs")
        self.logs_tab = LogsTab(logs_frame, self.manager, self.root)
        self.logs_tab.setup()

    def _setup_tray(self):
        """Setup system tray icon."""
        if not HAS_TRAY:
            return

        self.tray_manager = TrayManager(
            on_show=self._restore_from_tray,
            on_start=self._start_backups_from_tray,
            on_quit=self._quit_app
        )
        self.tray_manager.create_icon()

    def _reload_config(self):
        """Reload configuration."""
        self.manager.reload_config()
        self._reload_all_tabs()
        messagebox.showinfo("Reloaded", "Configuration reloaded successfully.")

    def _reload_all_tabs(self):
        """Reload all tabs after configuration changes."""
        # Reload backup tab
        if self.backup_tab:
            self.backup_tab.reload()

        # Reload config tab
        if self.config_tab:
            self.config_tab.reload()

        # Reload logs tab
        if self.logs_tab:
            self.logs_tab.reload()

        # Update backup count
        backup_count = len(self.manager.get_backup_sets())
        self.backup_count_label.config(text=f"{backup_count} backup(s) configured")

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

    def _view_log_file(self):
        """Open the main log file."""
        from constants import LOG_FILE
        if not LOG_FILE.exists():
            messagebox.showinfo("No Log File", "Log file does not exist yet.")
            return

        if IS_WINDOWS:
            os.startfile(LOG_FILE)
        else:
            subprocess.Popen(['xdg-open', str(LOG_FILE)])

    def _on_minimize(self, event):
        """Handle window minimize event."""
        # Ensure event is for the main window
        if event.widget != self.root:
            return

        # Check if window is minimized (iconic)
        if self.root.state() == 'iconic':
            if self.minimize_to_tray_enabled.get():
                if HAS_TRAY and self.tray_manager and not self.is_minimized_to_tray:
                    # Hide the window (remove from taskbar)
                    self.root.withdraw()
                    self.is_minimized_to_tray = True
                    self.tray_manager.run()

    def _restore_from_tray(self, icon=None, item=None):
        """Restore window from tray.
        
        Args:
            icon: Icon object (unused).
            item: Menu item (unused).
        """
        self.root.deiconify()
        self.root.lift()
        self.is_minimized_to_tray = False

    def _start_backups_from_tray(self, icon=None, item=None):
        """Start backups from tray menu.
        
        Args:
            icon: Icon object (unused).
            item: Menu item (unused).
        """
        if self.backup_tab:
            self.backup_tab._start_all()

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
        """Quit the application.
        
        Args:
            icon: Icon object (unused).
            item: Menu item (unused).
        """
        if self.tray_manager:
            self.tray_manager.stop()

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

        import sys
        sys.exit(0)

    def _toggle_tray_enabled(self):
        """Toggle the minimize-to-tray setting."""
        # Flip the value
        current = self.minimize_to_tray_enabled.get()
        self.minimize_to_tray_enabled.set(not current)
        
        # Persist to config
        from config_manager import save_config
        try:
            self.manager.config['app_settings']['minimize_to_tray'] = self.minimize_to_tray_enabled.get()
            save_config(self.manager.config)
            
            status = "enabled" if self.minimize_to_tray_enabled.get() else "disabled"
            messagebox.showinfo("Tray Setting", f"Minimize to tray is now {status}.")
        except Exception as e:
            logger.error(f"Failed to save tray setting: {e}")
            messagebox.showerror("Error", "Could not save tray setting.")

    def _toggle_dark_mode(self):
        """Toggle between light and dark themes."""
        if not HAS_TTK_BOOTSTRAP:
            messagebox.showinfo("Not Available", "Modern theming is not available.")
            return

        new_theme = DARK_THEME if self.current_theme == DEFAULT_THEME else DEFAULT_THEME
        
        try:
            # Apply new theme
            self.root.style.theme_use(new_theme)
            self.current_theme = new_theme
            
            # Persist to config
            from config_manager import save_config
            self.manager.config['app_settings']['theme'] = new_theme
            save_config(self.manager.config)
            
            logger.info(f"Switched to theme: {new_theme}")
        except Exception as e:
            logger.error(f"Failed to switch theme: {e}")
            messagebox.showerror("Error", "Could not switch theme.")

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
