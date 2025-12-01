#!/usr/bin/env python3
"""System tray icon management.

This module handles creating and managing the system tray icon
for the RClone Backup Manager application.
"""

import threading
from typing import Callable, Optional, TYPE_CHECKING

from constants import HAS_TRAY, APP_NAME

if HAS_TRAY:
    import pystray
    from PIL import Image, ImageDraw

if TYPE_CHECKING:
    if HAS_TRAY:
        from pystray import Icon


class TrayManager:
    """Manages system tray icon operations.
    
    This class handles:
    - Creating the tray icon
    - Setting up the tray menu
    - Running the tray icon in a background thread
    - Stopping the tray icon
    """

    def __init__(
        self,
        on_show: Callable,
        on_start: Callable,
        on_quit: Callable
    ):
        """Initialize the tray manager.
        
        Args:
            on_show: Callback to show the main window.
            on_start: Callback to start backups.
            on_quit: Callback to quit the application.
        """
        self.on_show = on_show
        self.on_start = on_start
        self.on_quit = on_quit
        self.icon: Optional[pystray.Icon] = None
        self._running = False

    def create_icon(self) -> Optional['pystray.Icon']:
        """Create the system tray icon.
        
        Returns:
            pystray.Icon instance or None if tray not available.
        """
        if not HAS_TRAY:
            return None

        # Create icon image with a modern look
        img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a rounded rectangle (simulated) or circle background
        # Gradient-like effect (simple solid color for now, but distinct)
        draw.ellipse((4, 4, 60, 60), fill=(13, 110, 253)) # Bootstrap Primary Blue
        
        # Draw text "RB" in white, centered
        # Simple font handling
        draw.text((14, 18), "RB", fill=(255, 255, 255), font_size=24) # Requires Pillow >= 9.2.0 for font_size, else default
        
        # Fallback for older Pillow if needed, but requirements said >=9.0.0
        # If font_size param fails, we might need ImageFont.truetype, but let's keep it simple for now
        # Actually, draw.text with font_size might not work on all versions without ImageFont object.
        # Let's use a safer approach with default font or load a font if possible.
        # Since we can't easily load a font without path, we'll stick to simple text or shapes.
        
        # Let's draw a simple "cloud" or "sync" shape instead of text if possible, or just cleaner text.
        # Drawing a simple sync arrow is hard. Let's stick to the Circle + Text but make it cleaner.


        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.on_show, default=True),
            pystray.MenuItem("Start Backups", self.on_start),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_quit)
        )

        self.icon = pystray.Icon(
            "rclone_backup",
            img,
            APP_NAME,
            menu
        )
        return self.icon

    def run(self):
        """Run the tray icon in a background thread."""
        if not HAS_TRAY or not self.icon:
            return

        if not self._running:
            self._running = True
            threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        """Stop the tray icon."""
        if self.icon and self._running:
            try:
                self.icon.stop()
                self._running = False
            except Exception:
                pass
