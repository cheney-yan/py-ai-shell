"""Update command for py-ai-shell."""

import subprocess
import sys

import click
from rich.console import Console

# Create a console for rich output
console = Console()

@click.command(name="update")
def update_command():
    """Update py-ai-shell to the latest version."""
    console.print("")
    command = "pip install --upgrade py-ai-shell"
    console.print(f"Running: {command}", style="dim")
    console.print("")

    try:
        subprocess.run(command, shell=True, check=True)
        console.print("\npy-ai-shell updated successfully!", style="green")
    except subprocess.CalledProcessError:
        console.print("\nFailed to update py-ai-shell.", style="red")
        sys.exit(1)
