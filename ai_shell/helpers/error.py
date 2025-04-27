"""Error handling for py-ai-shell."""

class KnownError(Exception):
    """Known error that should be displayed to the user."""
    pass

class ExitShellException(Exception):
    """Exception to signal that the shell should exit."""
    pass

def handle_cli_error(error):
    """Handle CLI errors."""
    # Import here to avoid circular imports
    import sys
    from rich.console import Console

    console = Console()

    # Check if this is an exit shell exception
    if isinstance(error, ExitShellException):
        # Exit directly without re-raising to avoid any error messages
        sys.exit(0)
    # Handle known errors by exiting immediately
    elif isinstance(error, KnownError):
        # Print the error message if it hasn't been printed already
        console.print(f"\n❌ {str(error)}", style="red")
        # Flush stdout to ensure the message is displayed
        sys.stdout.flush()
        # Exit with error code 1
        sys.exit(1)
    else:
        # Log the error or handle it in some way
        # For now, just print the error and continue
        console.print(f"\n❌ Unexpected error: {str(error)}", style="red")
