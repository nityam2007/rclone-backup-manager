# State Manager | Python
"""Persistent state management for backup history and statistics."""

import json
from datetime import datetime
from typing import Dict, List, Optional

from ..utils.constants import STATE_FILE, logger


class StateManager:
    """Manages persistent application state."""

    def __init__(self):
        self._state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from file."""
        if not STATE_FILE.exists():
            return self._get_default_state()

        try:
            with STATE_FILE.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return self._get_default_state()

    def _get_default_state(self) -> Dict:
        """Return default state structure."""
        return {
            "last_runs": {},
            "run_history": [],
            "statistics": {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0
            }
        }

    def save(self) -> bool:
        """Save state to file."""
        try:
            STATE_FILE.parent.mkdir(exist_ok=True)
            with STATE_FILE.open('w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            return False

    def record_run(self, name: str, success: bool, duration: float):
        """Record a backup run."""
        timestamp = datetime.now().isoformat()
        
        # Update last run
        self._state['last_runs'][name] = {
            'timestamp': timestamp,
            'success': success,
            'duration': duration
        }
        
        # Add to history (keep last 100)
        self._state['run_history'].append({
            'name': name,
            'timestamp': timestamp,
            'success': success,
            'duration': duration
        })
        self._state['run_history'] = self._state['run_history'][-100:]
        
        # Update statistics
        self._state['statistics']['total_runs'] += 1
        if success:
            self._state['statistics']['successful_runs'] += 1
        else:
            self._state['statistics']['failed_runs'] += 1
        
        self.save()

    def get_last_run(self, name: str) -> Optional[Dict]:
        """Get last run info for a backup."""
        return self._state['last_runs'].get(name)

    def get_last_run_time(self, name: str) -> str:
        """Get formatted last run time."""
        last_run = self.get_last_run(name)
        if not last_run:
            return "Never"
        
        try:
            dt = datetime.fromisoformat(last_run['timestamp'])
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return "Unknown"

    def get_statistics(self) -> Dict:
        """Get backup statistics."""
        return self._state['statistics']

    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get recent backup history."""
        return self._state['run_history'][-limit:][::-1]
