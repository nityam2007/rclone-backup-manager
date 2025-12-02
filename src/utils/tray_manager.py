# System Tray Manager | Python
"""System tray icon management for background operation."""

import threading
from typing import Callable, Optional

from .constants import HAS_TRAY, APP_NAME

if HAS_TRAY:
    import pystray
    from PIL import Image, ImageDraw


class TrayManager:
    """Manages system tray icon and menu."""

    def __init__(
        self,
        on_show: Callable,
        on_start: Callable,
        on_quit: Callable
    ):
        self.on_show = on_show
        self.on_start = on_start
        self.on_quit = on_quit
        self.icon: Optional['pystray.Icon'] = None
        self._running = False

    def _create_icon_image(self) -> 'Image.Image':
        """Create a modern tray icon."""
        size = 64
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background circle with gradient effect
        draw.ellipse((2, 2, size-2, size-2), fill=(13, 110, 253))
        draw.ellipse((4, 4, size-4, size-4), fill=(30, 125, 255))
        
        # Inner circle for depth
        inner_margin = 12
        draw.ellipse(
            (inner_margin, inner_margin, size-inner_margin, size-inner_margin),
            fill=(255, 255, 255, 40)
        )
        
        # Draw sync arrows icon
        arrow_color = (255, 255, 255)
        # Simplified arrow representation
        draw.polygon([(20, 32), (32, 20), (32, 28), (44, 28), (44, 36), (32, 36), (32, 44)], fill=arrow_color)
        
        return img

    def create_icon(self) -> Optional['pystray.Icon']:
        """Create and configure the system tray icon."""
        if not HAS_TRAY:
            return None

        img = self._create_icon_image()

        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self.on_show, default=True),
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
        """Start the tray icon in a background thread."""
        if not HAS_TRAY or not self.icon:
            return

        if not self._running:
            self._running = True
            thread = threading.Thread(target=self.icon.run, daemon=True)
            thread.start()

    def stop(self):
        """Stop and remove the tray icon."""
        if self.icon and self._running:
            try:
                self.icon.stop()
                self._running = False
            except Exception:
                pass

    def update_tooltip(self, text: str):
        """Update the tray icon tooltip text."""
        if self.icon:
            self.icon.title = text
