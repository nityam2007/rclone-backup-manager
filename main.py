#!/usr/bin/env python3
"""RClone Backup Manager - Main Entry Point.

A beautiful, production-ready cross-platform GUI for managing rclone backups
with modern tabbed interface and automated scheduling.

Author: Nityam (https://github.com/Nityam2007)
Repository: https://github.com/Nityam2007/rclone-backup-manager
License: Public Domain (Unlicense)
Version: 2.0.0
"""

import argparse
import platform
import sys
from pathlib import Path

from constants import APP_NAME, VERSION, HAS_TK, HAS_TRAY, CFG_FILE, LOG_FILE, logger
from backup_manager import BackupManager
from main_window import MainWindow


def main():
    """Main entry point for the RClone Backup Manager application."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} v{VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'{APP_NAME} v{VERSION}'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file (default: folders.json in script directory)'
    )

    args = parser.parse_args()

    # Override config file if specified
    if args.config:
        import constants
        constants.CFG_FILE = Path(args.config).resolve()

    logger.info(f"Starting {APP_NAME} v{VERSION}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Config file: {CFG_FILE}")
    logger.info(f"Log file: {LOG_FILE}")

    # Check for tkinter
    if not HAS_TK:
        print("ERROR: tkinter not available. Please install python3-tk")
        sys.exit(1)

    # Warn if tray not available
    if not HAS_TRAY:
        logger.warning("pystray/Pillow not available. System tray disabled.")

    # Create backup manager
    manager = BackupManager()

    # Create and run GUI
    try:
        app = MainWindow(manager)
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
