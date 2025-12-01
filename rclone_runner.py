#!/usr/bin/env python3
"""RClone command execution module.

This module handles executing rclone commands with progress tracking,
platform-specific handling, and error management.
"""

import re
import shlex
import subprocess
from typing import List, Optional, Callable

from constants import IS_WINDOWS, logger


def run_rclone_copy(
    local: str,
    remote: str,
    extras: List[str],
    progress_callback: Optional[Callable[[float, str], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None
) -> int:
    """Execute rclone copy with progress tracking.
    
    Args:
        local: Local path to backup.
        remote: Remote destination path.
        extras: Additional rclone command-line arguments.
        progress_callback: Optional callback for progress updates (percent, line).
        log_callback: Optional callback for log messages.
        
    Returns:
        Exit code from rclone command (0 = success).
    """
    cmd = ['rclone', 'copy', local, remote, '--progress'] + extras

    if IS_WINDOWS:
        # Windows-specific handling
        cmd_str = subprocess.list2cmdline(cmd)
    else:
        cmd_str = ' '.join(shlex.quote(x) for x in cmd)

    logger.info(f'Running: {cmd_str}')
    if log_callback:
        log_callback(f'Command: {cmd_str}\n')

    try:
        # Use different encoding on Windows
        encoding = 'utf-8' if not IS_WINDOWS else 'cp437'

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=encoding,
            errors='replace'
        )

        percent = 0.0
        for line in p.stdout:
            line = line.rstrip('\n')
            if log_callback:
                log_callback(line + '\n')

            if progress_callback:
                # Try to extract percentage
                m = re.search(r'(\d{1,3})%', line)
                if m:
                    try:
                        percent = float(m.group(1))
                    except ValueError:
                        pass
                progress_callback(percent, line)

        rc = p.wait()
        if progress_callback:
            progress_callback(100.0, f'Finished (exit code: {rc})')
        if log_callback:
            log_callback(f'\n=== Finished with exit code: {rc} ===\n\n')

        return rc

    except FileNotFoundError:
        error_msg = "ERROR: rclone not found. Please install rclone and ensure it's in PATH"
        logger.error(error_msg)
        if log_callback:
            log_callback(error_msg + '\n')
        if progress_callback:
            progress_callback(0, error_msg)
        return 127
    except Exception as e:
        error_msg = f'ERROR: {e}'
        logger.exception(error_msg)
        if log_callback:
            log_callback(error_msg + '\n')
        if progress_callback:
            progress_callback(percent, error_msg)
        return 1
