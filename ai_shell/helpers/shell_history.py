"""Shell history integration for AI Shell."""

import os
import platform

def get_history_file():
    """Get the shell history file path."""
    home = os.path.expanduser("~")
    
    # Different history files for different shells and platforms
    if platform.system() == "Windows":
        # PowerShell history
        return os.path.join(home, "AppData", "Roaming", "Microsoft", "Windows", "PowerShell", "PSReadLine", "ConsoleHost_history.txt")
    else:
        # Check for different shells on Unix-like systems
        shell = os.path.basename(os.environ.get("SHELL", ""))
        if shell == "zsh":
            return os.path.join(home, ".zsh_history")
        elif shell == "bash":
            return os.path.join(home, ".bash_history")
        elif shell == "fish":
            return os.path.join(home, ".local", "share", "fish", "fish_history")
    
    # Default to bash history if we can't determine
    return os.path.join(home, ".bash_history")

def get_last_command(history_file):
    """Get the last command from the history file."""
    try:
        with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
            commands = f.read().strip().split("\n")
            return commands[-1] if commands else None
    except Exception:
        # Ignore any errors
        return None

def append_to_shell_history(command):
    """Append the command to the shell history file."""
    history_file = get_history_file()
    if history_file:
        last_command = get_last_command(history_file)
        if last_command != command:
            try:
                with open(history_file, "a", encoding="utf-8") as f:
                    f.write(f"{command}\n")
            except Exception:
                # Ignore any errors
                pass
