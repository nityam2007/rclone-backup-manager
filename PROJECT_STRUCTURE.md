# Project Structure

```
rclone-backup-manager/
├── .github/
│   └── workflows/
│       └── build.yml              # GitHub Actions for automated builds
├── backup_gui.py                  # Main application (single file ~1450 lines)
├── build/                         # Build artifacts (gitignored)
├── dist/                          # Distribution executables (gitignored)
├── .gitignore                     # Git ignore rules
├── CHANGELOG.md                   # Version history and changes
├── CONTRIBUTING.md                # Contribution guidelines
├── folders.json.example           # Example configuration file
├── INSTALL.md                     # Detailed installation guide
├── LICENSE                        # Public Domain (Unlicense)
├── PROJECT_STRUCTURE.md           # This file
├── QUICKSTART.md                  # 5-minute quick start guide
├── README.md                      # Main documentation
├── rclone_backup_gui.spec         # PyInstaller build specification
├── requirements.txt               # Python dependencies
└── setup.sh                       # Automated setup script (Linux)
```

## Runtime Files (Created on First Run)

These files are created automatically when you run the application:

```
├── backup_gui.log                 # Application logs
├── folders.json                   # Your backup configuration
└── .first_run_done                # First run flag (for --checksum)
```

## Build Artifacts (Gitignored)

When building executables, these directories are created:

```
├── build/                         # PyInstaller build cache
├── dist/                          # Distribution executables
└── __pycache__/                   # Python bytecode cache
```

## Key Files Explained

### `backup_gui.py`
The entire application in a single Python file (~1450 lines). Contains:
- GUI implementation using Tkinter
- Backup manager with multi-threading
- Configuration management
- System tray integration
- Logging and progress tracking

### `folders.json`
JSON configuration file storing:
- Backup sets (name, local path, remote path)
- rclone settings (transfers, checkers, retries)
- App settings (tray, auto-run)

### `rclone_backup_gui.spec`
PyInstaller specification for building standalone executables.

### Documentation Files
- **README.md**: Comprehensive documentation with story-like presentation
- **QUICKSTART.md**: Get running in 5 minutes
- **INSTALL.md**: Detailed installation for all platforms
- **CONTRIBUTING.md**: How to contribute to the project
- **CHANGELOG.md**: Version history and changes

## Building from Source

```bash
# Clone repository
git clone https://github.com/Nityam2007/rclone-backup-manager.git
cd rclone-backup-manager

# Install dependencies
pip install -r requirements.txt

# Run from source
python backup_gui.py

# Build executable
pip install pyinstaller
pyinstaller rclone_backup_gui.spec
```

## Distribution

The `dist/backup_gui/` folder contains everything needed to run the application:
- Executable file
- Required libraries
- No Python installation needed!

Simply zip this folder and distribute to users.
