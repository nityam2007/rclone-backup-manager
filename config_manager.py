#!/usr/bin/env python3
"""Configuration management."""

import json
from typing import Dict

from constants import CFG_FILE, logger


def get_default_config() -> Dict:
    """Return default configuration structure."""
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
            "theme": "cosmo"
        }
    }


def load_config() -> Dict:
    """Load configuration from JSON file."""
    if not CFG_FILE.exists():
        default_config = get_default_config()
        save_config(default_config)
        return default_config

    try:
        with CFG_FILE.open('r', encoding='utf-8') as f:
            config = json.load(f)

        # Ensure settings exist
        if 'settings' not in config:
            config['settings'] = {
                "transfers": 8,
                "checkers": 8,
                "retries": 3,
                "retries_sleep": "10s"
            }

        # Ensure app_settings exist
        if 'app_settings' not in config:
            config['app_settings'] = {
                "minimize_to_tray": True,
                "start_minimized": False,
                "auto_run_enabled": False,
                "auto_run_interval_min": 5,
                "theme": "cosmo"
            }
        
        # Ensure new keys exist
        if 'start_minimized' not in config['app_settings']:
            config['app_settings']['start_minimized'] = False
            
        if 'dry_run' not in config['app_settings']:
            config['app_settings']['dry_run'] = False
        
        # Ensure theme exists in app_settings
        if 'theme' not in config['app_settings']:
            config['app_settings']['theme'] = "cosmo"

        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return get_default_config()


def save_config(config: Dict) -> bool:
    """Save configuration to JSON file."""
    try:
        with CFG_FILE.open('w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False
