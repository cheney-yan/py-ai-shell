"""Configuration command for py-ai-shell."""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from ..helpers.config import get_config, set_configs
from ..helpers.error import KnownError

# Create a console for rich output
console = Console()

@click.group(name="config")
def config_command():
    """Configure py-ai-shell."""
    pass

@config_command.command(name="get")
@click.argument("key", required=False)
def config_get(key: str = None):
    """Get configuration values."""
    try:
        config = get_config()

        if key:
            if key.upper() not in config:
                raise KnownError(f"Invalid config property: {key}")

            console.print(f"{key.upper()}={config[key.upper()]}")
        else:
            for k, v in config.items():
                # Don't print the API key
                if k == "OPENAI_KEY":
                    v = "********"
                console.print(f"{k}={v}")
    except Exception as e:
        console.print(f"❌ {str(e)}", style="red")
        # Exit immediately on error
        import sys
        sys.exit(1)

@config_command.command(name="set")
@click.argument("key_values", nargs=-1)
def config_set(key_values):
    """Set configuration values."""
    try:
        if not key_values:
            # Interactive mode
            choice = Prompt.ask(
                "Which configuration do you want to set?",
                choices=["OPENAI_KEY", "OPENAI_API_ENDPOINT", "MODEL", "SILENT_MODE", "LANGUAGE"],
                default="OPENAI_KEY"
            )

            if choice == "OPENAI_KEY":
                key = Prompt.ask("Enter your OpenAI API key")
                set_configs([("OPENAI_KEY", key)])
            elif choice == "OPENAI_API_ENDPOINT":
                endpoint = Prompt.ask("Enter your OpenAI API Endpoint", default="https://api.openai.com/v1")
                set_configs([("OPENAI_API_ENDPOINT", endpoint)])
            elif choice == "MODEL":
                model = Prompt.ask("Enter the model to use", default="gpt-4.1-nano")
                set_configs([("MODEL", model)])
            elif choice == "SILENT_MODE":
                silent = Confirm.ask("Enable silent mode?")
                set_configs([("SILENT_MODE", str(silent).lower())])
            elif choice == "LANGUAGE":
                language = Prompt.ask("Enter the language code", default="en")
                set_configs([("LANGUAGE", language)])
        else:
            # Parse key=value pairs
            pairs = []
            for kv in key_values:
                if "=" not in kv:
                    raise KnownError(f"Invalid format: {kv}. Use KEY=VALUE format.")

                key, value = kv.split("=", 1)
                pairs.append((key.upper(), value))

            set_configs(pairs)

        console.print("Configuration updated successfully!", style="green")
    except Exception as e:
        console.print(f"❌ {str(e)}", style="red")
        # Exit immediately on error
        import sys
        sys.exit(1)