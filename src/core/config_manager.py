# Configuration Manager | Python
"""Configuration file handling for backup sets and settings."""

import json
from typing import Dict

from ..utils.constants import CFG_FILE, logger


def get_default_config() -> Dict:
    """Return the default configuration structure."""
    return {
        "backup_sets": [],
        "settings": {
            "transfers": 8,
            "checkers": 8,
            "retries": 3,
            "retries_sleep": "10s"
        },
        "app_settings": {
            "minimize_to_tray": True,
            "start_minimized": False,
            "auto_run_enabled": False,
            "auto_run_interval_min": 5,
            "dry_run": False,
            "theme": "cosmo",
            "show_notifications": True
        }
    }


def load_config() -> Dict:
    """Load configuration from the JSON file."""
    if not CFG_FILE.exists():
        default_config = get_default_config()
        save_config(default_config)
        return default_config

    try:
        with CFG_FILE.open('r', encoding='utf-8') as f:
            config = json.load(f)

        # Ensure all required sections exist
        default = get_default_config()
        
        if 'settings' not in config:
            config['settings'] = default['settings']
        
        if 'app_settings' not in config:
            config['app_settings'] = default['app_settings']
        else:
            # Merge missing keys from default
            for key, value in default['app_settings'].items():
                if key not in config['app_settings']:
                    config['app_settings'][key] = value

        if 'backup_sets' not in config:
            config['backup_sets'] = []

        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return get_default_config()
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return get_default_config()


def save_config(config: Dict) -> bool:
    """Save configuration to the JSON file."""
    try:
        with CFG_FILE.open('w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info("Configuration saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False


def validate_backup_set(backup_set: Dict) -> tuple[bool, str]:
    """Validate a backup set configuration."""
    if not backup_set.get('name'):
        return False, "Name is required"
    if not backup_set.get('local'):
        return False, "Local path is required"
    if not backup_set.get('remote'):
        return False, "Remote path is required"
    if ':' not in backup_set.get('remote', ''):
        return False, "Remote must include rclone remote name (e.g., myremote:path)"
    return True, ""
