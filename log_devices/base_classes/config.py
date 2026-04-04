# -*- coding: utf-8 -*-

import os
from pathlib import Path

import yaml


class ConfigDict(dict):
    """Wrapper class to provide configparser-like interface for YAML config"""

    def __init__(self, config_dict):
        super().__init__()
        self.update(config_dict)

    def __getitem__(self, key):
        return super().__getitem__(key)

    def getint(self, section, key):
        return int(super().__getitem__(section)[key])

    def getfloat(self, section, key):
        return float(super().__getitem__(section)[key])

    def get(self, section, key=None):
        if key is None:
            return super().get(section)
        return super().__getitem__(section).get(key)


def load_config(config_filename="config.yaml"):
    """
    Load YAML configuration from the config directory.

    Args:
        config_filename (str): Name of the configuration file (default: config.yaml)

    Returns:
        dict: Configuration dictionary
    """
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
    config_path = os.path.join(config_dir, config_filename)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def get_config_value(config, *keys, default=None):
    """
    Safely get nested configuration values.

    Args:
        config (dict): Configuration dictionary
        *keys: Nested keys to access
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    value = config
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    return value if value is not None else default
