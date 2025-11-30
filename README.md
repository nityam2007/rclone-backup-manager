# 🚀 RClone Backup Manager

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-Public%20Domain-brightgreen.svg)

**A beautiful, production-ready GUI for managing your rclone backups with ease**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Screenshots](#-screenshots)

</div>

---

## 📖 The Story

Picture this: You have important files scattered across your computer, and you want them safely backed up to the cloud. You've heard about **rclone** - the Swiss Army knife of cloud storage - but the command line feels intimidating. You want something simple, visual, and reliable.

**Enter RClone Backup Manager** 🎯

This isn't just another backup tool. It's your personal backup assistant that:
- **Speaks your language** - No more cryptic commands, just click and backup
- **Works while you sleep** - Set it once, and it runs automatically every 5 minutes
- **Stays out of your way** - Minimizes to system tray, quietly protecting your data
- **Shows you everything** - Real-time progress bars, detailed logs, and status updates
- **Never forgets** - Tracks when each backup last ran, so you're always informed

Built with love using Python and Tkinter, this single-file application (~1400 lines) packs enterprise-grade features into a lightweight, cross-platform package.

---

## ✨ Features

### 🎨 **Beautiful Modern Interface**
- **Tabbed Design**: Organize backups, configuration, and logs in separate tabs
- **Real-time Progress**: Watch your backups happen with live progress bars
- **Color-coded Status**: Green for success, red for errors, gray for idle
- **Last Run Tracking**: See exactly when each backup last completed

### ⚡ **Powerful Automation**
- **Auto-Run Mode**: Schedule backups to run every 5 minutes automatically
- **Dry Run Testing**: Test your backup configurations without copying files
- **Multi-threaded**: Run multiple backups in parallel for maximum speed
- **Smart First Run**: Uses `--checksum` on first backup for accuracy

### 🛠️ **Easy Configuration**
- **Visual Editor**: Add, edit, and delete backups through a friendly GUI
- **Folder Browser**: No typing paths - just click and select
- **JSON Backend**: All settings stored in human-readable `folders.json`
- **Live Reload**: Changes take effect with a single F5 press

### 🔔 **System Integration**
- **System Tray**: Minimize to tray and keep running in background (Windows & Linux)
- **Notifications**: Get notified when "Run Once" backups complete
- **Keyboard Shortcuts**: F5 to reload, Ctrl+Q to quit
- **Cross-platform**: Works seamlessly on Windows and Linux

### 📊 **Comprehensive Logging**
- **Per-backup Logs**: Each backup maintains its own detailed log
- **Auto-refresh**: Logs update every 2 seconds during active backups
- **Timestamp Tracking**: Start time, end time, and duration for every backup
- **Error Reporting**: Clear exit codes and error messages

---

## 🎯 Quick Start

### Prerequisites

Before you begin, ensure you have:
- **Python 3.7+** installed
- **rclone** installed and configured ([rclone.org](https://rclone.org))
- **tkinter** (usually comes with Python, but see installation notes)

### Installation

#### Option 1: Run from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Nityam2007/rclone-backup-manager.git
cd rclone-backup-manager

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python backup/backup_gui.py
```

#### Option 2: Build Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable (creates dist/backup_gui)
pyinstaller rclone_backup_gui.spec

# Run the executable
./dist/backup_gui/backup_gui  # Linux
# or
dist\backup_gui\backup_gui.exe  # Windows
```

### First-Time Setup

1. **Configure rclone** (if not already done):
   ```bash
   rclone config
   ```
   Follow the prompts to add your cloud storage provider (Google Drive, Dropbox, S3, etc.)

2. **Launch RClone Backup Manager**:
   ```bash
   python backup/backup_gui.py
   ```

3. **Add Your First Backup**:
   - Click the **Configuration** tab
   - Click **Add New Backup**
   - Fill in:
     - **Name**: e.g., "My Documents"
     - **Local Folder**: Browse to select folder (e.g., `/home/user/Documents`)
     - **Remote Path**: Your rclone remote (e.g., `gdrive:Backups/Documents`)
   - Click **Add**
   - Click **Save All Changes**

4. **Test Your Backup**:
   - Go to **Backups** tab
   - Check **Dry Run** (to test without copying)
   - Click **Start All Now**
   - Watch the progress and check logs!

5. **Enable Auto-Run** (Optional):
   - Check **Auto-Run Every 5 Min** to enable automatic backups
   - Check **Minimize to Tray** to run in background

---

## 📚 Documentation

### Configuration File Structure

The application stores all settings in `folders.json`:

```json
{
  "backup_sets": [
    {
      "name": "My Documents",
      "local": "/home/user/Documents",
      "remote": "gdrive:Backups/Documents"
    },
    {
      "name": "Photos",
      "local": "/home/user/Pictures",
      "remote": "gdrive:Backups/Photos"
    }
  ],
  "settings": {
    "transfers": 8,
    "checkers": 8,
    "retries": 3,
    "retries_sleep": "10s"
  },
  "app_settings": {
    "minimize_to_tray": true,
    "auto_run_enabled": false,
    "auto_run_interval_min": 5
  }
}
```

### Understanding Remote Paths

RClone uses a `remote:path` format:
- **remote**: The name you gave during `rclone config`
- **path**: The folder path on that remote

Examples:
- `gdrive:Backups` - Google Drive, Backups folder
- `dropbox:Work/Projects` - Dropbox, Work/Projects folder
- `s3:mybucket/data` - Amazon S3, mybucket/data

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Reload configuration |
| `Ctrl+Q` | Exit application |
| `Tab` | Switch between tabs |
| `Esc` | Close dialogs |

### Command-Line Options

```bash
# Show version
python backup/backup_gui.py --version

# Use custom config file
python backup/backup_gui.py --config /path/to/custom.json

# Show help
python backup/backup_gui.py --help
```

---

## 🖼️ Screenshots

### Main Backup Interface
The main interface shows all your configured backups with real-time progress bars, status indicators, and last run timestamps.

### Configuration Editor
Add, edit, and manage your backup sets through an intuitive form-based interface - no manual JSON editing required!

### Live Logs Viewer
Monitor your backups in real-time with auto-refreshing logs that show every detail of the rclone operation.

---

## 🔧 Advanced Usage

### Running as a Service (Linux)

Create a systemd service to run backups automatically:

```bash
# Create service file
sudo nano /etc/systemd/system/rclone-backup.service
```

```ini
[Unit]
Description=RClone Backup Manager
After=network.target

[Service]
Type=simple
User=yourusername
Environment=DISPLAY=:0
ExecStart=/usr/bin/python3 /path/to/backup/backup_gui.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable rclone-backup
sudo systemctl start rclone-backup
```

### Customizing rclone Settings

Edit the `settings` section in `folders.json`:

- **transfers**: Number of parallel file transfers (default: 8)
- **checkers**: Number of parallel file checkers (default: 8)
- **retries**: Number of retry attempts on errors (default: 3)
- **retries_sleep**: Time to wait between retries (default: "10s")

Higher values = faster but more resource-intensive.

### Building for Distribution

```bash
# Install build dependencies
pip install pyinstaller pillow pystray

# Build single-file executable
pyinstaller --onefile --windowed --name rclone-backup-manager backup/backup_gui.py

# Executable will be in dist/
```

---

## 🐛 Troubleshooting

### "rclone not found" Error
**Solution**: Install rclone and ensure it's in your system PATH
```bash
# Linux
sudo apt install rclone  # Debian/Ubuntu
sudo dnf install rclone  # Fedora

# Or download from rclone.org
```

### "tkinter not available" Error
**Solution**: Install tkinter
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### System Tray Not Working
**Solution**: Install pystray and Pillow
```bash
pip install pystray pillow
```

### Backups Not Running Automatically
1. Check that **Auto-Run Every 5 Min** is checked
2. Verify `folders.json` has `"auto_run_enabled": true`
3. Check logs in `backup_gui.log` for errors

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/Nityam2007/rclone-backup-manager.git
cd rclone-backup-manager

# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Run the application
python backup/backup_gui.py
```

---

## 📋 Requirements

### Python Packages
- `tkinter` (GUI framework - usually included with Python)
- `pystray` (system tray support - optional)
- `Pillow` (image support for tray icon - optional)

### System Requirements
- **Python**: 3.7 or higher
- **rclone**: Latest version recommended
- **OS**: Windows 7+ or Linux (Ubuntu 18.04+, Fedora 30+, etc.)
- **RAM**: 100MB minimum
- **Disk**: 50MB for application + space for logs

---

## 📜 License

This project is released into the **Public Domain**. 

You are free to:
- ✅ Use commercially
- ✅ Modify and distribute
- ✅ Use privately
- ✅ Use without attribution (though it's appreciated!)

No warranty is provided. Use at your own risk.

---

## 🙏 Acknowledgments

- **[rclone](https://rclone.org)** - The amazing cloud storage sync tool that powers this application
- **Python Tkinter** - For the cross-platform GUI framework
- **pystray** - For system tray integration
- **The Open Source Community** - For inspiration and support

---

## 📞 Contact & Support

- **GitHub**: [@Nityam2007](https://github.com/Nityam2007)
- **Repository**: [rclone-backup-manager](https://github.com/Nityam2007/rclone-backup-manager)
- **Issues**: [Report a bug](https://github.com/Nityam2007/rclone-backup-manager/issues)

---

<div align="center">

**Made with ❤️ by Nityam**

If this project helped you, consider giving it a ⭐ on GitHub!

[⬆ Back to Top](#-rclone-backup-manager)

</div>
