# Changelog

All notable changes to RClone Backup Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-11-30

### Added
- **Last Backup Timestamp Tracking**: Each backup now displays when it last ran
- **Custom Dialog Windows**: Fixed large font size issue in Help, About, and Documentation dialogs
- **Improved UI**: Better visual feedback with color-coded status indicators
- **Enhanced Logging**: Start time, end time, and duration tracking for all backups
- **Professional Branding**: Complete GitHub repository setup with comprehensive documentation

### Changed
- Improved dialog window presentation with proper font sizing (10pt)
- Enhanced status display with last run time information
- Better error reporting and user feedback

### Fixed
- Large font size in dialog windows (Help, About, Documentation)
- Missing timestamp information in backup logs
- UI consistency across different system configurations

## [1.0.0] - Initial Release

### Added
- Cross-platform GUI for rclone backups (Windows & Linux)
- Modern tabbed interface (Backups, Configuration, Logs)
- Visual configuration editor - no manual JSON editing
- System tray support with minimize to tray
- Auto-run mode - backups every 5 minutes
- Real-time progress tracking with progress bars
- Detailed per-backup logging with auto-refresh
- Dry run mode for testing
- Multi-threaded parallel backup operations
- Smart first-run with checksum verification
- Keyboard shortcuts (F5 to reload, Ctrl+Q to quit)
- Folder browser for easy path selection
- PyInstaller support for standalone executables
- Comprehensive error handling and logging
