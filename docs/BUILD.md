# How to Build

Want to build the app yourself? It's actually pretty easy. Here is how you do it.

## What you need

- **Python 3.9+** installed.
- **Git** to download the code.

## Steps

1.  **Get the code**:
    ```bash
    git clone https://github.com/Nityam2007/rclone-backup-manager.git
    cd rclone-backup-manager
    ```

2.  **Install the build tools**:
    We use `pyinstaller` to package the app.
    ```bash
    pip install -r requirements.txt
    pip install pyinstaller
    ```

3.  **Build it**:
    Run this command in your terminal:
    ```bash
    pyinstaller rclone_backup.spec
    ```

4.  **Done!**
    You will find your shiny new executable in the `dist/rclone-backup-manager` folder.
    - On **Windows**, look for `rclone-backup-manager.exe`.
    - On **Linux**, look for the `rclone-backup-manager` binary.

That's it! 🚀
