"""Error handling for AI Shell."""

class KnownError(Exception):
    """Known error that should be displayed to the user."""
    pass

class ExitShellException(Exception):
    """Exception to signal that the shell should exit."""
    pass

def handle_cli_error(error):
    """Handle CLI errors."""
    # Check if this is an exit shell exception
    if isinstance(error, ExitShellException):
        # Exit directly without re-raising to avoid any error messages
        import sys
        sys.exit(0)
    # This can be expanded later with more specific error handling
    elif isinstance(error, KnownError):
        # Already formatted for display
        pass
    else:
        # Log the error or handle it in some way
        pass
