"""Update command for AI Shell."""

import subprocess
import sys

import click
from rich.console import Console

# Create a console for rich output
console = Console()

@click.command(name="update")
def update_command():
    """Update AI Shell to the latest version."""
    console.print("")
    command = "pip install --upgrade ai-shell"
    console.print(f"Running: {command}", style="dim")
    console.print("")
    
    try:
        subprocess.run(command, shell=True, check=True)
        console.print("\nAI Shell updated successfully!", style="green")
    except subprocess.CalledProcessError:
        console.print("\nFailed to update AI Shell.", style="red")
        sys.exit(1)
