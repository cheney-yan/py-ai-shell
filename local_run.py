#!/usr/bin/env python3
"""Test script for AI Shell with hot reloading."""

import sys
import os
import time
import importlib
import traceback
from pathlib import Path
from typing import Dict

# Add the current directory to the path so we can import the ai_shell package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_shell.cli import main
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from rich.console import Console

# Create a console for rich output
console = Console()

# Track loaded modules to avoid reloading the same module multiple times
_loaded_modules: Dict[str, float] = {}
_module_map: Dict[str, str] = {}

class ModuleReloader(FileSystemEventHandler):
    """File system event handler that reloads Python modules when they change."""

    def __init__(self, package_dir: str):
        """Initialize the module reloader."""
        self.package_dir = Path(package_dir).resolve()
        self.package_name = self.package_dir.name
        self._build_module_map()

    def _build_module_map(self) -> None:
        """Build a map of file paths to module names."""
        global _module_map

        for root, _, files in os.walk(self.package_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, os.path.dirname(self.package_dir))
                    module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                    _module_map[file_path] = module_name

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith('.py'):
            self._reload_module(event.src_path)

    def _reload_module(self, file_path: str) -> None:
        """Reload a module when its source file changes."""
        global _loaded_modules

        # Avoid reloading the same module multiple times in quick succession
        current_time = time.time()
        if file_path in _loaded_modules:
            if current_time - _loaded_modules[file_path] < 1.0:
                return

        _loaded_modules[file_path] = current_time

        # Get the module name from the file path
        module_name = _module_map.get(file_path)
        if not module_name:
            return

        # Check if the module is loaded
        if module_name not in sys.modules:
            return

        # Reload the module
        try:
            console.print(f"[yellow]Hot reloading module: {module_name}[/yellow]")
            module = sys.modules[module_name]
            importlib.reload(module)
            console.print(f"[green]Successfully reloaded: {module_name}[/green]")
        except Exception as e:
            console.print(f"[red]Error reloading module {module_name}:[/red]")
            console.print(f"[red]{str(e)}[/red]")
            console.print(traceback.format_exc())

if __name__ == "__main__":
    # Set up hot reloading for the ai_shell package
    package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_shell")

    # Create an observer and event handler for hot reloading
    observer = Observer()
    event_handler = ModuleReloader(package_dir)

    # Schedule the observer to watch the package directory
    observer.schedule(event_handler, package_dir, recursive=True)

    # Start the observer in a daemon thread
    observer.daemon = True
    observer.start()

    console.print(f"[green]Hot reload started. Watching: {package_dir}[/green]")

    try:
        # Run the main CLI function
        main()
    finally:
        # Ensure the observer is stopped when the program exits
        if observer:
            observer.stop()
            observer.join()
