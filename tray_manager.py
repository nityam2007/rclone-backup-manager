#!/usr/bin/env python3
"""System tray icon management."""

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
    """Manages system tray icon operations."""

    def __init__(
        self,
        on_show: Callable,
        on_start: Callable,
        on_quit: Callable
    ):
        self.on_show = on_show
        self.on_start = on_start
        self.on_quit = on_quit
        self.icon: Optional[pystray.Icon] = None
        self._running = False

    def create_icon(self) -> Optional['pystray.Icon']:
        """Create the system tray icon."""
        if not HAS_TRAY:
            return None

        # Create icon image
        img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw background circle (Bootstrap Primary Blue)
        draw.ellipse((4, 4, 60, 60), fill=(13, 110, 253))
        
        # Draw text "RB"
        # Note: font_size requires Pillow >= 9.2.0
        try:
            draw.text((14, 18), "RB", fill=(255, 255, 255), font_size=24)
        except TypeError:
            # Fallback for older Pillow versions
            draw.text((20, 24), "RB", fill=(255, 255, 255))

        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.on_show, default=True),
            pystray.MenuItem("Start All Backups", self.on_start),
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
