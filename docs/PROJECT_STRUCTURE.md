# Project Structure

```
rclone-backup-manager/
├── main.py                        # Entry point
├── main_window.py                 # Main GUI window
├── backup_manager.py              # Backup logic and threading
├── config_manager.py              # Configuration handling
├── tray_manager.py                # System tray integration
├── ui_components.py               # Reusable UI widgets
├── constants.py                   # Global constants
├── backup_tab.py                  # Backup operations tab
├── config_tab.py                  # Configuration editor tab
├── logs_tab.py                    # Logs viewer tab
├── folders.json                   # Your configuration (created on run)
├── backup_gui.log                 # Application logs (created on run)
├── requirements.txt               # Dependencies
└── README.md                      # Documentation
```

## Key Files

- **main.py**: Starts the application.
- **backup_manager.py**: Handles the actual `rclone` commands and background threads.
- **folders.json**: Stores your backup sets and settings.
