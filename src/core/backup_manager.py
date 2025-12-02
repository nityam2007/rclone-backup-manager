# Backup Manager | Python
"""Core backup operations manager."""

import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Optional

from ..utils.constants import FIRST_RUN_FLAG, logger
from .config_manager import load_config
from .rclone_runner import run_rclone_copy
from .state_manager import StateManager


class BackupManager:
    """Manages backup operations, status tracking, and scheduling."""

    def __init__(self):
        self.config = load_config()
        self.state = StateManager()
        self.threads: Dict[str, threading.Thread] = {}
        self.status: Dict[str, Dict] = {}
        self.logs: Dict[str, List[str]] = {}
        self.lock = threading.Lock()
        self.stop_requested = False
        self._on_complete_callbacks: List[Callable] = []

    def reload_config(self):
        """Reload configuration from file."""
        self.config = load_config()
        logger.info("Configuration reloaded")

    def get_backup_sets(self) -> List[Dict]:
        """Get all configured backup sets."""
        return self.config.get('backup_sets', [])

    def get_settings(self) -> Dict:
        """Get rclone settings."""
        return self.config.get('settings', {})

    def get_app_settings(self) -> Dict:
        """Get application settings."""
        return self.config.get('app_settings', {})

    def on_backup_complete(self, callback: Callable):
        """Register a callback for backup completion."""
        self._on_complete_callbacks.append(callback)

    def start_all(self, dry_run: bool = False):
        """Start all configured backup operations."""
        self.stop_requested = False
        settings = self.get_settings()

        # Build rclone arguments
        extras = [
            f'--transfers={settings.get("transfers", 8)}',
            f'--checkers={settings.get("checkers", 8)}',
            f'--retries={settings.get("retries", 3)}',
            f'--retries-sleep={settings.get("retries_sleep", "10s")}',
            '--stats-one-line'
        ]

        # First run uses checksum for accuracy
        first_run = not FIRST_RUN_FLAG.exists()
        if first_run:
            extras.append('--checksum')
            logger.info("First run detected, using --checksum for accuracy")

        if dry_run:
            extras.append('--dry-run')
            logger.info("Dry run mode enabled")

        for backup_set in self.get_backup_sets():
            name = backup_set.get('name', 'unnamed')
            local = backup_set.get('local', '')
            remote = backup_set.get('remote', '')

            if not local or not remote:
                logger.warning(f"Skipping {name}: missing local or remote path")
                continue

            # Initialize status
            with self.lock:
                self.status[name] = {
                    'percent': 0,
                    'line': 'Initializing...',
                    'rc': None,
                    'start_time': datetime.now().isoformat()
                }
                self.logs[name] = []

            thread = threading.Thread(
                target=self._run_backup,
                args=(name, local, remote, extras),
                daemon=True
            )
            self.threads[name] = thread
            thread.start()

        # Mark first run complete
        if first_run and self.get_backup_sets():
            FIRST_RUN_FLAG.write_text(datetime.utcnow().isoformat())

    def _run_backup(self, name: str, local: str, remote: str, extras: List[str]):
        """Execute a single backup operation."""
        start_time = datetime.now()

        def progress_cb(percent: float, line: str):
            with self.lock:
                self.status[name]['percent'] = percent
                self.status[name]['line'] = line

        def log_cb(line: str):
            with self.lock:
                self.logs[name].append(line)

        # Log header
        log_cb(f"{'='*60}\n")
        log_cb(f"Backup: {name}\n")
        log_cb(f"Source: {local}\n")
        log_cb(f"Target: {remote}\n")
        log_cb(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_cb(f"{'='*60}\n\n")

        # Adjust remote path if needed
        try:
            remote_path = remote.split(':', 1)[1] if ':' in remote else ''
            if remote_path and '/' not in remote_path:
                remote = f"{remote.rstrip('/')}/{Path(local).name}"
        except Exception:
            pass

        logger.info(f"Starting: {name} ({local} -> {remote})")
        
        rc = run_rclone_copy(local, remote, extras, progress_cb, log_cb)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Update status
        with self.lock:
            self.status[name] = {
                'percent': 100.0,
                'line': 'Completed successfully' if rc == 0 else f'Failed (exit code: {rc})',
                'rc': rc,
                'duration': duration
            }

        # Log footer
        log_cb(f"\n{'='*60}\n")
        log_cb(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_cb(f"Duration: {duration:.1f}s\n")
        log_cb(f"Status: {'SUCCESS' if rc == 0 else 'FAILED'}\n")
        log_cb(f"{'='*60}\n")

        # Record in state
        self.state.record_run(name, rc == 0, duration)

        logger.info(f"Completed: {name} (exit code: {rc}, duration: {duration:.1f}s)")

        # Notify callbacks
        for callback in self._on_complete_callbacks:
            try:
                callback(name, rc == 0)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def get_status(self) -> Dict:
        """Get current status of all backups."""
        with self.lock:
            return dict(self.status)

    def get_logs(self, name: str) -> str:
        """Get logs for a specific backup."""
        with self.lock:
            return ''.join(self.logs.get(name, []))

    def get_last_run_time(self, name: str) -> str:
        """Get formatted last run time for a backup."""
        return self.state.get_last_run_time(name)

    def is_running(self) -> bool:
        """Check if any backup is currently running."""
        with self.lock:
            for name, s in self.status.items():
                if s.get('rc') is None:
                    return True
        return False

    def get_running_count(self) -> int:
        """Get count of currently running backups."""
        count = 0
        with self.lock:
            for s in self.status.values():
                if s.get('rc') is None:
                    count += 1
        return count

    def get_statistics(self) -> Dict:
        """Get backup statistics."""
        return self.state.get_statistics()
