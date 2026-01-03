"""Configuration management for VocalNode."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages application configuration."""
    
    DEFAULT_CONFIG = {
        "hotkey": {
            "key": "f8",
            "modifiers": [],
            "mode": "toggle"  # "toggle" or "hold"
        },
        "stt": {
            "model": "base",
            "language": "en",
            "device": "cpu"  # "cpu" or "cuda"
        },
        "audio": {
            "device_id": None,  # None = default device
            "sample_rate": 16000,
            "channels": 1
        },
        "overlay": {
            "enabled": True,
            "position": "bottom_right",  # "top_left", "top_right", "bottom_left", "bottom_right", "center"
            "show_text": True,
            "opacity": 0.9
        },
        "text_insertion": {
            "method": "typing",  # "typing" or "clipboard"
            "typing_delay": 0.01
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            config_dir = Path.home() / ".vocalnode"
            config_dir.mkdir(exist_ok=True)
            config_path = config_dir / "config.json"
        
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                # Merge with defaults to ensure all keys exist
                self._merge_defaults()
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _merge_defaults(self) -> None:
        """Merge loaded config with defaults to ensure all keys exist."""
        def merge_dict(default: Dict, loaded: Dict) -> Dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        self.config = merge_dict(self.DEFAULT_CONFIG, self.config)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., "hotkey.key")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., "hotkey.key")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save()

