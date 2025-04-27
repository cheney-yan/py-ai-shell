"""Command-line interface for py-ai-shell."""

import sys
import signal
import asyncio
from typing import Optional, List

import click
from rich.console import Console

from .helpers.constants import PROJECT_NAME, COMMAND_NAME
from .helpers.error import handle_cli_error
from .prompt import prompt as ai_prompt, in_ai_interaction
from .commands.config import config_command
from .commands.update import update_command

# Create a console for rich output
console = Console()

# Global flag to track if we're in a command execution
in_command_execution = False

# Handle Ctrl+C
def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    global in_command_execution

    if in_ai_interaction:
        console.print("\nAI interaction stopped by user.", style="yellow")
        # Don't exit, just stop the current interaction
        # The flag will be reset in the finally block of the prompt function
    elif in_command_execution:
        console.print("\nCommand execution stopped by user.", style="yellow")
        # The subprocess will be terminated by the OS
        in_command_execution = False
    else:
        # If we're not in an AI interaction or command execution,
        # just print a message and continue
        console.print("\nUse Ctrl+D to exit AI Shell.", style="yellow")

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

@click.command(context_settings=dict(ignore_unknown_options=True))
@click.version_option()
@click.option("--prompt", "-p", help="Prompt to run")
@click.option("--silent", "-s", is_flag=True, help="Less verbose, skip printing the command explanation")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(ctx, prompt: Optional[str] = None, silent: bool = False, args: List[str] = None):
    """AI-powered shell assistant."""
    # Handle positional arguments as prompt
    if args:
        # Join all arguments into a single prompt
        prompt_text = " ".join(args)

        # Handle special commands
        if prompt_text.strip() == "update":
            update_command()
            return
        elif prompt_text.strip() == "config":
            config_command()
            return
        elif prompt_text.startswith("config "):
            # Parse config subcommands
            config_args = prompt_text[7:].split()
            if config_args and config_args[0] == "set":
                config_set_args = config_args[1:]
                from .commands.config import config_set
                config_set(config_set_args)
                return
            elif config_args and config_args[0] == "get":
                config_get_arg = config_args[1] if len(config_args) > 1 else None
                from .commands.config import config_get
                config_get(config_get_arg)
                return

        # Use the joined arguments as the prompt
        prompt = prompt_text

    # If --prompt option is provided, it takes precedence
    if not prompt and ctx.params.get("prompt"):
        prompt = ctx.params["prompt"]

    # Run the main prompt loop
    try:
        # Add a counter to prevent infinite loops on repeated errors
        consecutive_errors = 0
        max_consecutive_errors = 3

        # Create a single event loop for the entire application
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            while True:
                try:
                    # Use the same event loop for all prompts
                    loop.run_until_complete(ai_prompt(use_prompt=prompt, silent_mode=silent))
                    # Clear prompt after first iteration so subsequent loops wait for user input
                    prompt = None
                    # Reset error counter on successful execution
                    consecutive_errors = 0
                except KeyboardInterrupt:
                    # Ctrl+C was handled by the signal handler, just continue the loop
                    continue
                except Exception as e:
                    # Import at the top level to avoid any import issues
                    from .helpers.error import ExitShellException

                    # First check if this is an exit request
                    if isinstance(e, ExitShellException):
                        # User pressed Ctrl+D, exit the shell without showing error
                        # The goodbye message is already printed in the get_prompt function
                        break

                    # For all other errors, print the error message
                    console.print(f"\n❌ {str(e)}", style="red")

                    # Increment error counter
                    consecutive_errors += 1

                    # If we've had too many consecutive errors, exit to prevent infinite loops
                    if consecutive_errors >= max_consecutive_errors:
                        console.print("\nToo many consecutive errors. Exiting py-ai-shell.", style="red")
                        break

                    # Add a small delay before retrying to prevent tight loops
                    import time
                    time.sleep(0.5)

                    # Handle errors properly
                    try:
                        # Skip error handling for ExitShellException
                        if not isinstance(e, ExitShellException):
                            # This will exit immediately for KnownError exceptions
                            handle_cli_error(e)
                    except Exception as handle_error:
                        # If error handling itself fails, print the error and continue
                        console.print(f"\nError handling failed: {str(handle_error)}", style="red")
        finally:
            # Clean up any pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()

            # Run the event loop until all tasks are done
            if pending:
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

            # Close the event loop
            loop.close()
    except KeyboardInterrupt:
        # This should not happen as we're handling Ctrl+C in the signal handler
        # But just in case, exit gracefully
        console.print("\nGoodbye!", style="cyan")
        sys.exit(0)

def main():
    """Entry point for the CLI."""
    cli(obj={})

if __name__ == "__main__":
    main()
