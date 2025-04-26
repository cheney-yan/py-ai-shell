"""Configuration management for AI Shell."""

import os
import configparser
from pathlib import Path

from .constants import COMMAND_NAME
from .error import KnownError

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".ai-shell")

def get_config():
    """Get the configuration."""
    config = configparser.ConfigParser()
    
    # Create default config
    config["DEFAULT"] = {
        "OPENAI_KEY": "",
        "OPENAI_API_ENDPOINT": "https://api.openai.com/v1",
        "MODEL": "gpt-4o-mini",
        "SILENT_MODE": "false",
        "LANGUAGE": "en",
    }
    
    # Read existing config if it exists
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
    
    # Validate config
    if not config["DEFAULT"]["OPENAI_KEY"]:
        raise KnownError(
            f"Please set your OpenAI API key via `{COMMAND_NAME} config set OPENAI_KEY=<your token>`"
        )
    
    return config["DEFAULT"]

def set_configs(key_values):
    """Set configuration values."""
    config = configparser.ConfigParser()
    
    # Read existing config if it exists
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)
    
    # Ensure DEFAULT section exists
    if "DEFAULT" not in config:
        config["DEFAULT"] = {}
    
    # Update config with new values
    for key, value in key_values:
        if key not in ["OPENAI_KEY", "OPENAI_API_ENDPOINT", "MODEL", "SILENT_MODE", "LANGUAGE"]:
            raise KnownError(f"Invalid config property: {key}")
        
        config["DEFAULT"][key] = value
    
    # Write config to file
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
