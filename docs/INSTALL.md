# Installation Guide

## Requirements
- Python 3.7+
- rclone (installed and in your PATH)

## Linux (Ubuntu/Debian)

1. **Install System Deps**:
   ```bash
   sudo apt update
   sudo apt install rclone python3-tk python3-pip
   ```

2. **Install App Deps**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run**:
   ```bash
   python3 main.py
   ```

## Windows

1. **Install Python**: Download from python.org.
2. **Install rclone**: Download from rclone.org and add it to your PATH.
3. **Install App Deps**:
   ```cmd
   pip install -r requirements.txt
   ```
4. **Run**:
   Double-click `main.py` or run `python main.py` in cmd.

## Building an Executable (Optional)

If you want a standalone .exe or binary:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name rclone-backup-manager main.py
```
The output will be in the `dist/` folder.
