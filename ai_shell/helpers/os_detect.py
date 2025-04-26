"""OS and shell detection utilities."""

import os
import platform

def detect_shell():
    """Detect the current shell."""
    try:
        # Detect if we're running on Windows and assume powershell
        if platform.system() == "Windows":
            return "powershell"
        
        # Otherwise return current shell; default to bash
        shell = os.environ.get("SHELL", "/bin/bash")
        return os.path.basename(shell)
    except Exception as err:
        raise Exception(f"Shell detection failed unexpectedly: {str(err)}")
