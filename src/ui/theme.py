# Theme Manager and Icons | Python
"""Modern theme management and SVG-style icon definitions."""

from typing import Dict

from ..utils.constants import HAS_TTK_BOOTSTRAP, COLORS


# Unicode icons for cross-platform compatibility
ICONS = {
    # Navigation
    'home': '\u2302',
    'settings': '\u2699',
    'menu': '\u2630',
    
    # Actions
    'play': '\u25B6',
    'stop': '\u25A0',
    'refresh': '\u21BB',
    'add': '\u002B',
    'remove': '\u2212',
    'delete': '\u2716',
    'edit': '\u270E',
    'save': '\u2714',
    'cancel': '\u2718',
    
    # Status
    'success': '\u2714',
    'error': '\u2718',
    'warning': '\u26A0',
    'info': '\u2139',
    'loading': '\u21BB',
    
    # Files & Folders
    'folder': '\u2750',
    'folder_open': '\u2751',
    'file': '\u2222',
    'cloud': '\u2601',
    'sync': '\u21C4',
    
    # UI Elements
    'expand': '\u25BC',
    'collapse': '\u25B2',
    'chevron_right': '\u276F',
    'chevron_left': '\u276E',
    'arrow_up': '\u2191',
    'arrow_down': '\u2193',
    
    # Misc
    'clock': '\u23F0',
    'calendar': '\u2752',
    'star': '\u2605',
    'heart': '\u2665',
    'bolt': '\u26A1',
    'shield': '\u2764',
    'link': '\u21D7',
    'external': '\u21D7',
    'copy': '\u21D2',
    'minimize': '\u2193',
    'maximize': '\u2197',
    'close': '\u2715',
}


class ThemeManager:
    """Manages application theming and colors."""
    
    THEMES = {
        'light': {
            'name': 'cosmo',
            'bg': '#ffffff',
            'fg': '#212529',
            'card_bg': '#f8f9fa',
            'border': '#dee2e6',
            'accent': '#0d6efd',
        },
        'dark': {
            'name': 'darkly',
            'bg': '#212529',
            'fg': '#f8f9fa',
            'card_bg': '#343a40',
            'border': '#495057',
            'accent': '#0d6efd',
        }
    }
    
    def __init__(self, root, initial_theme: str = 'light'):
        self.root = root
        self.current_theme = initial_theme
        
    def get_theme(self) -> Dict:
        """Get current theme configuration."""
        return self.THEMES.get(self.current_theme, self.THEMES['light'])
    
    def toggle_theme(self) -> str:
        """Toggle between light and dark themes."""
        if not HAS_TTK_BOOTSTRAP:
            return self.current_theme
            
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.current_theme = new_theme
        
        theme_config = self.THEMES[new_theme]
        try:
            self.root.style.theme_use(theme_config['name'])
        except Exception:
            pass
            
        return new_theme
    
    def apply_theme(self, theme_name: str):
        """Apply a specific theme."""
        if not HAS_TTK_BOOTSTRAP:
            return
            
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            theme_config = self.THEMES[theme_name]
            try:
                self.root.style.theme_use(theme_config['name'])
            except Exception:
                pass


def get_status_color(status: str) -> str:
    """Get color for a status type."""
    status_colors = {
        'success': COLORS['success'],
        'error': COLORS['danger'],
        'warning': COLORS['warning'],
        'info': COLORS['info'],
        'running': COLORS['primary'],
        'idle': COLORS['muted'],
    }
    return status_colors.get(status, COLORS['text_primary'])


def get_progress_style(percent: float) -> str:
    """Get progress bar style based on completion."""
    if percent >= 100:
        return 'success'
    elif percent >= 50:
        return 'info'
    elif percent >= 25:
        return 'warning'
    return 'primary'
