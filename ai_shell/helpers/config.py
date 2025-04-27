"""Configuration management for py-ai-shell."""

import os
import configparser

from .constants import COMMAND_NAME

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".config", "py-ai-shell", "config.ini")

def get_config():
    """Get the configuration."""
    config = configparser.ConfigParser()

    # Create default config
    config["DEFAULT"] = {
        "OPENAI_KEY": "",
        "OPENAI_API_ENDPOINT": "https://api.openai.com/v1",
        "MODEL": "gpt-4.1-nano",
        "SILENT_MODE": "false",
        "LANGUAGE": "en",
    }

    # Read existing config if it exists
    if os.path.exists(CONFIG_PATH):
        config.read(CONFIG_PATH)

    # Validate config
    if not config["DEFAULT"]["OPENAI_KEY"]:
        # Import here to avoid circular imports
        from rich.console import Console
        import sys

        # Create a new console instance for this error message
        console = Console()

        # Print the error message
        error_message = f"❌ Please set your OpenAI API key via `{COMMAND_NAME} config set OPENAI_KEY=<your token>`"
        console.print(error_message, style="red")

        # Flush stdout to ensure the message is displayed
        sys.stdout.flush()

        # Exit immediately with error code 1
        sys.exit(1)

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
            # Import here to avoid circular imports
            from rich.console import Console
            import sys

            # Create a new console instance for this error message
            console = Console()

            # Print the error message
            error_message = f"❌ Invalid config property: {key}"
            console.print(error_message, style="red")

            # Flush stdout to ensure the message is displayed
            sys.stdout.flush()

            # Exit immediately with error code 1
            sys.exit(1)

        config["DEFAULT"][key] = value

    # Ensure the config directory exists
    config_dir = os.path.dirname(CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)

    # Write config to file
    with open(CONFIG_PATH, "w") as f:
        config.write(f)
