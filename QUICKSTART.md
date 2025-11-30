# Quick Start Guide - RClone Backup Manager

Get up and running in 5 minutes! 🚀

## Step 1: Install rclone

### Linux
```bash
sudo apt install rclone  # Debian/Ubuntu
# or
curl https://rclone.org/install.sh | sudo bash
```

### Windows
Download from [rclone.org/downloads](https://rclone.org/downloads/) and add to PATH.

## Step 2: Configure rclone

```bash
rclone config
```

Choose your cloud provider (Google Drive, Dropbox, etc.) and follow the prompts.

**Example for Google Drive:**
1. Type `n` for new remote
2. Name it `gdrive`
3. Choose `drive` for Google Drive
4. Follow authentication steps
5. Type `q` to quit

## Step 3: Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/Nityam2007/rclone-backup-manager.git
cd rclone-backup-manager

# Install dependencies
pip3 install -r requirements.txt

# Linux only: Install tkinter if needed
sudo apt install python3-tk  # Debian/Ubuntu
```

## Step 4: Run the Application

```bash
python3 backup/backup_gui.py
```

## Step 5: Add Your First Backup

1. Click the **Configuration** tab
2. Click **Add New Backup**
3. Fill in:
   - **Name**: "My Documents"
   - **Local Folder**: Click Browse → Select your Documents folder
   - **Remote Path**: `gdrive:Backups/Documents` (use your remote name from Step 2)
4. Click **Add**
5. Click **Save All Changes**

## Step 6: Test Your Backup

1. Go to **Backups** tab
2. ✅ Check **Dry Run** (this tests without copying)
3. Click **Start All Now**
4. Watch the progress bar!
5. Check the **Logs** tab to see details

## Step 7: Enable Auto-Run (Optional)

1. Uncheck **Dry Run**
2. ✅ Check **Auto-Run Every 5 Min**
3. ✅ Check **Minimize to Tray**
4. Minimize the window - it will run in the background!

---

## Common Remote Path Examples

| Cloud Provider | Remote Name | Example Path |
|---------------|-------------|--------------|
| Google Drive | `gdrive` | `gdrive:Backups/MyFolder` |
| Dropbox | `dropbox` | `dropbox:Backups/MyFolder` |
| OneDrive | `onedrive` | `onedrive:Backups/MyFolder` |
| Amazon S3 | `s3` | `s3:mybucket/backups` |
| Local Disk | N/A | `/mnt/external/backups` |

---

## Troubleshooting

### "rclone not found"
```bash
# Check if rclone is installed
rclone version

# If not, install it (see Step 1)
```

### "No module named 'tkinter'"
```bash
# Linux
sudo apt install python3-tk
```

### "Permission denied"
```bash
# Make script executable (Linux)
chmod +x backup/backup_gui.py
```

---

## Next Steps

- 📖 Read the full [README.md](README.md)
- 🔧 Check [INSTALL.md](INSTALL.md) for detailed installation
- 🐛 Report issues on [GitHub](https://github.com/Nityam2007/rclone-backup-manager/issues)

**Happy backing up! 🎉**
