import json
import os
from typing import Dict, Any

CONFIG_FILE = os.path.expanduser("~/.tarqim_config.json")

class ConfigManager:
    @staticmethod
    def load_config() -> Dict[str, Any]:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @staticmethod
    def save_config(config: Dict[str, Any]):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass

    @staticmethod
    def get_pinned_files() -> list:
        config = ConfigManager.load_config()
        return config.get("pinned_files", [])

    @staticmethod
    def add_pinned_file(path: str):
        config = ConfigManager.load_config()
        pinned = config.get("pinned_files", [])
        if path not in pinned:
            pinned.append(path)
            config["pinned_files"] = pinned
            ConfigManager.save_config(config)

    @staticmethod
    def remove_pinned_file(path: str):
        config = ConfigManager.load_config()
        pinned = config.get("pinned_files", [])
        if path in pinned:
            pinned.remove(path)
            config["pinned_files"] = pinned
            ConfigManager.save_config(config)

    @staticmethod
    def is_pinned(path: str) -> bool:
        config = ConfigManager.load_config()
        pinned = config.get("pinned_files", [])
        return path in pinned
