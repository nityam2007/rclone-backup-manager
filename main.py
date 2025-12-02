#!/usr/bin/env python3
# RClone Backup Manager - Entry Point | Python
"""RClone Backup Manager - A modern GUI for rclone backup operations."""

import argparse
import platform
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.constants import APP_NAME, VERSION, HAS_TK, HAS_TRAY, CFG_FILE, LOG_FILE, logger
from src.core.backup_manager import BackupManager
from src.ui.main_window import MainWindow


def main():
    """Application entry point."""
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
        help='Path to custom config file'
    )

    args = parser.parse_args()

    # Custom config path
    if args.config:
        from src.utils import constants
        constants.CFG_FILE = Path(args.config).resolve()

    logger.info(f"Starting {APP_NAME} v{VERSION}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Config: {CFG_FILE}")
    logger.info(f"Log: {LOG_FILE}")

    if not HAS_TK:
        print("ERROR: tkinter not available. Please install python3-tk")
        sys.exit(1)

    if not HAS_TRAY:
        logger.warning("pystray/Pillow not available. System tray disabled.")

    # Initialize and run
    try:
        manager = BackupManager()
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
