# Changelog

All notable changes to RClone Backup Manager will be documented in this file.

## [2.3.0] - 2025-12-07
### Added
- **Cross-Platform Fonts**: Native fonts on Windows (Segoe UI), macOS (SF Pro), Linux (Ubuntu)
- **Consistent Spacing**: Unified spacing system throughout the UI

### Fixed
- **Minimize to Tray**: Button now works correctly after restoring from tray
- **PyInstaller Spec**: Fully self-contained build with all dependencies bundled

### Changed
- **Version**: Bumped to v2.3.0 for production-ready UI release

## [2.1.2] - 2025-12-01
### Added
- **Minimize to Tray**: Dedicated button in Backup tab.
- **Start Minimized**: Option to start the application silently in the tray.
- **Single Instance**: Prevents multiple instances from running simultaneously.
- **Configurable Settings**: Dry Run and Auto-Run settings now persist in the Config tab.
- **Scrolling Support**: Mouse wheel scrolling for backup lists and dialogs.

### Fixed
- **Linux Build**: Fixed build process to use correct spec file.
- **Tray Behavior**: Robust minimize-to-tray logic for Linux and Windows.
- **UI Consistency**: Unified dialog styling.

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
