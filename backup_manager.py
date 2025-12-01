#!/usr/bin/env python3
"""Backup operations manager."""

import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from constants import FIRST_RUN_FLAG, logger
from config_manager import load_config
from rclone_runner import run_rclone_copy


class BackupManager:
    """Manages backup operations and tracks their status."""

    def __init__(self):
        self.config = load_config()
        self.threads: Dict[str, threading.Thread] = {}
        self.status: Dict[str, Dict] = {}
        self.logs: Dict[str, List[str]] = {}
        self.last_run_times: Dict[str, str] = {}
        self.lock = threading.Lock()
        self.stop_requested = False

    def reload_config(self):
        """Reload configuration from file."""
        self.config = load_config()
        logger.info("Configuration reloaded")

    def get_backup_sets(self) -> List[Dict]:
        return self.config.get('backup_sets', [])

    def get_settings(self) -> Dict:
        return self.config.get('settings', {})

    def start_all(self, dry_run: bool = False):
        """Start all backup operations."""
        self.stop_requested = False
        settings = self.get_settings()

        # Build rclone arguments
        extras = [
            f'--transfers={settings.get("transfers", 8)}',
            f'--checkers={settings.get("checkers", 8)}',
            f'--retries={settings.get("retries", 3)}',
            f'--retries-sleep={settings.get("retries_sleep", "10s")}'
        ]

        # First run optimization
        first_run = not FIRST_RUN_FLAG.exists()
        if first_run:
            extras.append('--checksum')
            logger.info("First run detected, using --checksum")

        if dry_run:
            extras.append('--dry-run')

        for backup_set in self.get_backup_sets():
            name = backup_set.get('name', 'unnamed')
            local = backup_set.get('local', '')
            remote = backup_set.get('remote', '')

            if not local or not remote:
                logger.warning(f"Skipping {name}: missing local or remote path")
                continue

            # Reset status
            with self.lock:
                self.status[name] = {'percent': 0, 'line': 'Starting...', 'rc': None}
                self.logs[name] = []

            t = threading.Thread(
                target=self._run_backup,
                args=(name, local, remote, extras),
                daemon=True
            )
            self.threads[name] = t
            t.start()

        if first_run:
            FIRST_RUN_FLAG.write_text(datetime.utcnow().isoformat())

    def _run_backup(self, name: str, local: str, remote: str, extras: List[str]):
        """Run a single backup operation."""
        start_time = datetime.now()
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

        def progress_cb(percent, line):
            with self.lock:
                self.status[name] = {'percent': percent, 'line': line, 'rc': None}

        def log_cb(line):
            with self.lock:
                self.logs[name].append(line)

        with self.lock:
            self.logs[name].append(f'\n=== Backup started at {start_time_str} ===\n')

        # Adjust remote path
        try:
            rhs_raw = remote.split(':', 1)[1] if ':' in remote else ''
        except Exception:
            rhs_raw = ''

        if '/' not in rhs_raw and rhs_raw:
            target_remote = f"{remote.rstrip('/')}/{Path(local).name}"
        else:
            target_remote = remote

        logger.info(f"Starting backup: {name} ({local} -> {target_remote}) at {start_time_str}")
        rc = run_rclone_copy(local, target_remote, extras, progress_cb, log_cb)

        end_time = datetime.now()
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        duration = (end_time - start_time).total_seconds()

        with self.lock:
            self.status[name] = {
                'percent': 100.0,
                'line': f'Completed (exit code: {rc})',
                'rc': rc
            }
            self.last_run_times[name] = end_time_str
            self.logs[name].append(f'\n=== Backup completed at {end_time_str} (duration: {duration:.1f}s) ===\n')

        logger.info(f"Backup completed: {name} (exit code: {rc}) at {end_time_str}")

    def get_status(self) -> Dict:
        """Get current status of all backups."""
        with self.lock:
            return dict(self.status)

    def get_logs(self, name: str) -> str:
        """Get logs for a specific backup."""
        with self.lock:
            return ''.join(self.logs.get(name, []))

    def get_last_run_time(self, name: str) -> str:
        """Get last run time for a specific backup."""
        with self.lock:
            return self.last_run_times.get(name, 'Never')

    def is_running(self) -> bool:
        """Check if any backup is currently running."""
        status = self.get_status()
        for name, s in status.items():
            if s.get('rc') is None and s.get('percent', 0) < 100:
                return True
        return False
