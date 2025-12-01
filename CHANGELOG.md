# Changelog

All notable changes to RClone Backup Manager will be documented in this file.

## [2.1.0] - 2025-12-01

### Added
- **Modern UI**: Completely revamped interface using `ttkbootstrap` with Light/Dark mode support.
- **Modular Architecture**: Refactored single-file script into a maintainable, multi-file Python package.
- **Tooltips**: Added helpful tooltips to all buttons and inputs.
- **Tray Control**: Toggle "Minimize to Tray" directly from the File menu.
- **Theme Toggle**: Switch between Cosmo (Light) and Darkly (Dark) themes on the fly.

### Changed
- **Documentation**: Rewrote all documentation (README, QUICKSTART, etc.) to be human-readable and concise.
- **Project Structure**: Organized code into `main_window.py`, `backup_manager.py`, `ui_components.py`, etc.
- **License**: Changed to a custom Source Available license (Free for personal use, no commercial redistribution).

### Fixed
- **UI Scaling**: Improved layout and widget spacing.
- **Import Errors**: Resolved circular dependency issues in the new modular structure.

## [2.0.0] - 2025-11-30

### Added
- **Last Backup Timestamp**: Tracks when each backup last ran.
- **Custom Dialogs**: Fixed font size issues in dialogs.
- **Status Indicators**: Color-coded status (Green/Red/Gray).

## [1.0.0] - Initial Release
- Basic GUI for rclone.
- Auto-run scheduler.
- System tray support.
