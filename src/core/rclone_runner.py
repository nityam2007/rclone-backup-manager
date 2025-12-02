# RClone Runner | Python
"""RClone command execution with progress tracking."""

import re
import shlex
import subprocess
from typing import List, Optional, Callable

from ..utils.constants import IS_WINDOWS, logger


def run_rclone_copy(
    local: str,
    remote: str,
    extras: List[str],
    progress_callback: Optional[Callable[[float, str], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None
) -> int:
    """Execute rclone copy with progress tracking.
    
    Args:
        local: Source path to backup
        remote: Destination rclone remote path
        extras: Additional rclone arguments
        progress_callback: Callback for progress updates (percent, message)
        log_callback: Callback for log lines
        
    Returns:
        Exit code (0 = success)
    """
    cmd = ['rclone', 'copy', local, remote, '--progress', '--stats=1s'] + extras

    cmd_str = subprocess.list2cmdline(cmd) if IS_WINDOWS else ' '.join(shlex.quote(x) for x in cmd)
    
    logger.info(f'Executing: {cmd_str}')
    if log_callback:
        log_callback(f'$ {cmd_str}\n\n')

    try:
        encoding = 'utf-8' if not IS_WINDOWS else 'cp437'

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=encoding,
            errors='replace'
        )

        percent = 0.0
        current_file = ""
        
        for line in process.stdout:
            line = line.rstrip('\n')
            if log_callback:
                log_callback(line + '\n')

            if progress_callback:
                # Extract percentage from various rclone output formats
                pct_match = re.search(r'(\d{1,3})%', line)
                if pct_match:
                    try:
                        percent = float(pct_match.group(1))
                    except ValueError:
                        pass
                
                # Extract current file being transferred
                file_match = re.search(r'Transferring:\s*(.+?)(?:,|$)', line)
                if file_match:
                    current_file = file_match.group(1).strip()
                
                # Build status message
                if current_file:
                    status = f"{percent:.0f}% - {current_file}"
                else:
                    status = line if line.strip() else f"{percent:.0f}%"
                
                progress_callback(percent, status)

        rc = process.wait()
        
        if progress_callback:
            if rc == 0:
                progress_callback(100.0, 'Completed successfully')
            else:
                progress_callback(percent, f'Failed (exit code: {rc})')
        
        if log_callback:
            status = "SUCCESS" if rc == 0 else "FAILED"
            log_callback(f'\n[{status}] Exit code: {rc}\n')

        return rc

    except FileNotFoundError:
        error = "rclone not found. Please install rclone and add to PATH."
        logger.error(error)
        if log_callback:
            log_callback(f'ERROR: {error}\n')
        if progress_callback:
            progress_callback(0, error)
        return 127

    except Exception as e:
        error = f'Unexpected error: {e}'
        logger.exception(error)
        if log_callback:
            log_callback(f'ERROR: {error}\n')
        if progress_callback:
            progress_callback(0, error)
        return 1


def check_rclone_installed() -> tuple[bool, str]:
    """Check if rclone is installed and get version."""
    try:
        result = subprocess.run(
            ['rclone', 'version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return True, version
        return False, "rclone returned error"
    except FileNotFoundError:
        return False, "rclone not installed"
    except Exception as e:
        return False, str(e)


def list_remotes() -> List[str]:
    """List configured rclone remotes."""
    try:
        result = subprocess.run(
            ['rclone', 'listremotes'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return [r.strip() for r in result.stdout.strip().split('\n') if r.strip()]
        return []
    except Exception:
        return []
