# RClone Backup Manager

A simple, modern GUI for managing rclone backups.

## Why this exists?

I built this because while **rclone** is amazing, using it via command line or setting up cron jobs isn't for everyone.

- **Not everyone is a sysadmin**: Bash scripts and cron jobs are powerful but can be a headache to manage and debug for normal users.
- **Cross-Platform**: With Windows 10 support ending, more people are moving to Linux (Ubuntu, etc.). This tool works on both Windows and Linux.
- **Save Money**: Most Windows backup tools are paid. This lets you use free storage tiers (like Google Drive's 15GB, S3, etc.) easily.
- **Visual Feedback**: It's nice to actually *see* your backup progress and logs, rather than hoping a silent background script worked.
- **Trust**: No proprietary formats. It just runs standard `rclone` commands that you can verify.

## Features

- **Modern GUI**: Clean interface using `ttkbootstrap` (Dark/Light mode).
- **Tray Integration**: Minimizes to system tray so it stays out of your way.
- **Auto-Run**: Built-in scheduler runs backups every 5 minutes (Startup registration is WIP).
- **Real-time Logs**: See exactly what files are being transferred.
- **Configurable**: Easy JSON-based configuration managed through the UI.

## Screenshots

*(Screenshots coming soon!)*

## Building from Source

Want to build the executable yourself? Check out [BUILD.md](BUILD.md).

## Prerequisites

1.  **Python 3.7+**
2.  **rclone**: Must be installed and configured (`rclone config`).
    - [Download rclone](https://rclone.org/downloads/)

## Installation

1.  Clone the repo:
    ```bash
    git clone https://github.com/Nityam2007/rclone-backup-manager.git
    cd rclone-backup-manager
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(On Linux, you might need `sudo apt install python3-tk`)*

3.  Run it:
    ```bash
    python main.py
    ```

## Usage

1.  **Configure**: Go to the **Configuration** tab. Add a new backup set (Name, Local Path, Remote Path).
    - *Remote Path* should match your rclone config (e.g., `gdrive:Backups`).
2.  **Test**: Go to **Backups** tab, check "Dry Run", and hit "Start All Now".
3.  **Automate**: Check "Auto-Run" and "Minimize to Tray".

## License

Source Available License. Free for personal use.

## Credits

Built with ❤️ by **Nityam**.

Special thanks to the AI assistants that helped write the code and docs:
- **Antigravity** (Google DeepMind)
- **Gemini** (Google)
- **Claude** (Anthropic)
- **GPT** (OpenAI)

And the tools that made it possible:
- **VSCode**
- **Python**

