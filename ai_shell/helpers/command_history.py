"""Command history tracking for AI Shell."""

import time
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CommandResult:
    """Command execution result."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    timestamp: float

# Maximum number of commands to keep in history
MAX_HISTORY_SIZE = 5

# Store command history
command_history: List[CommandResult] = []

def add_to_command_history(result: CommandResult) -> None:
    """Add a command result to the history."""
    # Add to the beginning of the list (most recent first)
    command_history.insert(0, result)
    
    # Trim history to maximum size
    if len(command_history) > MAX_HISTORY_SIZE:
        command_history.pop()

def get_command_history() -> List[CommandResult]:
    """Get the command history."""
    return command_history.copy()

def clear_command_history() -> None:
    """Clear the command history."""
    command_history.clear()

def trim_output(output: str, max_lines: int) -> str:
    """Trim output to a maximum number of lines."""
    lines = output.split('\n')
    if len(lines) <= max_lines:
        return output
    
    # Keep first few lines and last few lines
    half_max = max_lines // 2
    first_half = lines[:half_max]
    second_half = lines[-half_max:]
    
    return '\n'.join([*first_half, f"... ({len(lines) - max_lines} more lines) ...", *second_half])

def format_command_history_for_ai() -> str:
    """Format command history as a string for AI context."""
    if not command_history:
        return "No command history available."
    
    # Create a more structured format with clear separation and numbering
    formatted_history = []
    for index, result in enumerate(command_history):
        command_number = len(command_history) - index  # Reverse numbering
        status_indicator = "✓" if result.exit_code == 0 else "✗"
        date = time.strftime("%H:%M:%S", time.localtime(result.timestamp))
        
        output = f"## Command {command_number} [{date}] {status_indicator}\n"
        output += f"```bash\n$ {result.command}\n```\n"
        output += f"Exit code: {result.exit_code}\n"
        
        if result.stdout and result.stdout.strip():
            trimmed_stdout = trim_output(result.stdout, 15)
            output += f"\nOutput:\n```\n{trimmed_stdout}\n```\n"
        
        if result.stderr and result.stderr.strip():
            trimmed_stderr = trim_output(result.stderr, 15)
            output += f"\nError:\n```\n{trimmed_stderr}\n```\n"
        
        formatted_history.append(output)
    
    return "\n".join(formatted_history)
