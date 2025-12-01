# Quick Start

Here is how to get your backups running quickly.

## 1. Setup rclone
If you haven't already, install rclone and set up a remote.
```bash
rclone config
```
Follow the prompts to add Google Drive, S3, or whatever cloud storage you use. Remember the name you give it (e.g., `gdrive`).

## 2. Install App
```bash
pip install -r requirements.txt
python main.py
```
*Linux users: You might need `sudo apt install python3-tk`.*

## 3. Add Backup
1. Open the **Configuration** tab.
2. Click **Add New Backup**.
3. **Local**: Pick the folder you want to backup.
4. **Remote**: Enter your rclone path (e.g., `gdrive:MyBackups`).
5. Click **Add** then **Save**.

## 4. Run
Go to the **Backups** tab and click **Start All Now**.
Use **Dry Run** first if you want to see what will happen without actually copying files.

## Auto-Run
Check **Auto-Run** to have it run every 5 minutes in the background. You can minimize the app to the tray.
*(Note: Adding the app to system startup is currently a manual process)*
