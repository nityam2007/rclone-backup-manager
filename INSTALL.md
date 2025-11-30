# RClone Backup Manager - Installation Guide

This guide will walk you through installing and setting up RClone Backup Manager on your system.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installing rclone](#installing-rclone)
- [Installing Python Dependencies](#installing-python-dependencies)
- [Running the Application](#running-the-application)
- [Building Standalone Executable](#building-standalone-executable)
- [Platform-Specific Notes](#platform-specific-notes)

---

## Prerequisites

### Required Software

1. **Python 3.7 or higher**
   - Check your version: `python3 --version`
   - Download from: [python.org](https://www.python.org/downloads/)

2. **rclone**
   - The backup engine that powers this application
   - Download from: [rclone.org](https://rclone.org/downloads/)

3. **pip** (Python package manager)
   - Usually comes with Python
   - Check: `pip3 --version`

---

## Installing rclone

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install rclone
```

### Linux (Fedora)
```bash
sudo dnf install rclone
```

### Linux (Manual Install)
```bash
curl https://rclone.org/install.sh | sudo bash
```

### Windows
1. Download from [rclone.org/downloads](https://rclone.org/downloads/)
2. Extract the ZIP file
3. Add rclone.exe to your PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Click "Environment Variables"
   - Edit "Path" and add the folder containing rclone.exe

### Verify Installation
```bash
rclone version
```

### Configure rclone
Before using the backup manager, configure at least one remote:
```bash
rclone config
```

Follow the interactive prompts to add your cloud storage (Google Drive, Dropbox, S3, etc.)

---

## Installing Python Dependencies

### Step 1: Clone the Repository
```bash
git clone https://github.com/Nityam2007/rclone-backup-manager.git
cd rclone-backup-manager
```

### Step 2: Install Required Packages

#### Linux
```bash
# Install tkinter (if not already installed)
sudo apt install python3-tk  # Debian/Ubuntu
sudo dnf install python3-tkinter  # Fedora

# Install Python packages
pip3 install -r requirements.txt
```

#### Windows
```bash
# tkinter usually comes with Python on Windows
# Just install Python packages
pip install -r requirements.txt
```

### Optional Dependencies

For **system tray support** (recommended):
```bash
pip3 install pystray pillow
```

If you skip this, the app will still work but won't have tray icon functionality.

---

## Running the Application

### From Source (Development Mode)

```bash
# Navigate to the project directory
cd rclone-backup-manager

# Run the application
python3 backup_gui.py
```

### With Custom Config File
```bash
python3 backup_gui.py --config /path/to/custom.json
```

### Check Version
```bash
python3 backup_gui.py --version
```

---

## Building Standalone Executable

Create a single executable file that doesn't require Python to be installed.

### Step 1: Install PyInstaller
```bash
pip3 install pyinstaller
```

### Step 2: Build the Executable

#### Using the Spec File (Recommended)
```bash
pyinstaller rclone_backup_gui.spec
```

#### Manual Build
```bash
pyinstaller --onefile \
            --windowed \
            --name rclone-backup-manager \
            --add-data "backup:backup" \
            backup_gui.py
```

### Step 3: Find Your Executable

The executable will be in:
- **Linux**: `dist/backup_gui/backup_gui`
- **Windows**: `dist\backup_gui\backup_gui.exe`

### Step 4: Run the Executable

#### Linux
```bash
cd dist/backup_gui
./backup_gui
```

#### Windows
```cmd
cd dist\backup_gui
backup_gui.exe
```

### Distribution

You can now distribute the entire `dist/backup_gui` folder to users who don't have Python installed!

---

## Platform-Specific Notes

### Linux

#### Desktop Entry (Optional)
Create a desktop shortcut:

```bash
nano ~/.local/share/applications/rclone-backup-manager.desktop
```

Add:
```ini
[Desktop Entry]
Type=Application
Name=RClone Backup Manager
Comment=Manage rclone backups with a GUI
Exec=/path/to/backup_gui.py
Icon=folder-sync
Terminal=false
Categories=Utility;System;
```

#### System Tray on Wayland
System tray support works best on X11. On Wayland, you may need:
```bash
sudo apt install gnome-shell-extension-appindicator  # Ubuntu/GNOME
```

### Windows

#### Run on Startup (Optional)
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create a shortcut to `backup_gui.exe` in this folder

#### Windows Defender
If Windows Defender blocks the executable:
1. Go to Windows Security → Virus & threat protection
2. Click "Manage settings"
3. Add an exclusion for the executable

---

## Troubleshooting

### "Command not found: python3"
**Windows**: Use `python` instead of `python3`
```cmd
python backup_gui.py
```

### "No module named 'tkinter'"
**Linux**: Install tkinter
```bash
sudo apt install python3-tk
```

### "rclone not found"
Ensure rclone is in your PATH:
```bash
which rclone  # Linux
where rclone  # Windows
```

### Permission Denied (Linux)
Make the script executable:
```bash
chmod +x backup_gui.py
```

### Import Errors
Reinstall dependencies:
```bash
pip3 install --force-reinstall -r requirements.txt
```

---

## Next Steps

1. ✅ **Configure rclone**: `rclone config`
2. ✅ **Run the application**: `python3 backup_gui.py`
3. ✅ **Add your first backup** in the Configuration tab
4. ✅ **Test with dry run** mode
5. ✅ **Enable auto-run** for hands-free backups

Need help? Check the [main README](README.md) or [open an issue](https://github.com/Nityam2007/rclone-backup-manager/issues)!
