"""Simple line editor for terminal applications.

This module provides a simple line editor for terminal applications.
It's based on the editor.py library by Wasim Lorgat (https://github.com/seeM/editor).
"""

import os
import sys
import termios
import tty
from typing import Callable, List, Optional, Tuple


def getch() -> str:
    """Read a single character from stdin."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_terminal_size() -> Tuple[int, int]:
    """Get the current terminal size."""
    return os.get_terminal_size()


def clear_line() -> None:
    """Clear the current line."""
    width = get_terminal_size()[0]
    sys.stdout.write("\r" + " " * width + "\r")
    sys.stdout.flush()


def edit(
    prompt: str = "",
    default: str = "",
    completer: Optional[Callable[[str, int], Tuple[List[str], int]]] = None,
) -> str:
    """Edit a line of text.

    Args:
        prompt: The prompt to display.
        default: The default text to edit.
        completer: A completer function.

    Returns:
        The edited text.
    """
    # Initialize state
    buffer = list(default)
    cursor_position = len(buffer)
    history = []
    history_position = 0

    # Display prompt and default text
    sys.stdout.write(prompt)
    sys.stdout.write("".join(buffer))
    sys.stdout.flush()

    while True:
        char = getch()

        # Handle special keys
        if char == "\x03":  # Ctrl+C
            raise KeyboardInterrupt
        elif char == "\x04":  # Ctrl+D
            if not buffer:
                raise EOFError
            else:
                continue
        elif char == "\x1b":  # Escape sequence
            next_char = getch()
            if next_char == "[":  # CSI
                command = getch()
                if command == "A":  # Up arrow
                    if history and history_position > 0:
                        history_position -= 1
                        clear_line()
                        sys.stdout.write(prompt)
                        buffer = list(history[history_position])
                        cursor_position = len(buffer)
                        sys.stdout.write("".join(buffer))
                        sys.stdout.flush()
                elif command == "B":  # Down arrow
                    if history and history_position < len(history) - 1:
                        history_position += 1
                        clear_line()
                        sys.stdout.write(prompt)
                        buffer = list(history[history_position])
                        cursor_position = len(buffer)
                        sys.stdout.write("".join(buffer))
                        sys.stdout.flush()
                elif command == "C":  # Right arrow
                    if cursor_position < len(buffer):
                        cursor_position += 1
                        sys.stdout.write("\x1b[C")
                        sys.stdout.flush()
                elif command == "D":  # Left arrow
                    if cursor_position > 0:
                        cursor_position -= 1
                        sys.stdout.write("\x1b[D")
                        sys.stdout.flush()
                elif command == "H":  # Home
                    sys.stdout.write("\r" + prompt)
                    cursor_position = 0
                    sys.stdout.flush()
                elif command == "F":  # End
                    sys.stdout.write("\r" + prompt + "".join(buffer))
                    cursor_position = len(buffer)
                    sys.stdout.flush()
                elif command == "3":  # Delete
                    if getch() == "~" and cursor_position < len(buffer):
                        buffer.pop(cursor_position)
                        clear_line()
                        sys.stdout.write(prompt + "".join(buffer))
                        sys.stdout.write("\r" + prompt + "".join(buffer[:cursor_position]))
                        sys.stdout.flush()
        elif char == "\x7f":  # Backspace
            if cursor_position > 0:
                cursor_position -= 1
                buffer.pop(cursor_position)
                clear_line()
                sys.stdout.write(prompt + "".join(buffer))
                sys.stdout.write("\r" + prompt + "".join(buffer[:cursor_position]))
                sys.stdout.flush()
        elif char == "\r":  # Enter
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(buffer)
        elif char == "\x01":  # Ctrl+A (beginning of line)
            sys.stdout.write("\r" + prompt)
            cursor_position = 0
            sys.stdout.flush()
        elif char == "\x05":  # Ctrl+E (end of line)
            sys.stdout.write("\r" + prompt + "".join(buffer))
            cursor_position = len(buffer)
            sys.stdout.flush()
        elif char == "\x0b":  # Ctrl+K (kill to end of line)
            buffer = buffer[:cursor_position]
            clear_line()
            sys.stdout.write(prompt + "".join(buffer))
            sys.stdout.flush()
        elif char == "\x15":  # Ctrl+U (kill to beginning of line)
            buffer = buffer[cursor_position:]
            cursor_position = 0
            clear_line()
            sys.stdout.write(prompt + "".join(buffer))
            sys.stdout.write("\r" + prompt)
            sys.stdout.flush()
        else:  # Regular character
            buffer.insert(cursor_position, char)
            cursor_position += 1
            clear_line()
            sys.stdout.write(prompt + "".join(buffer))
            sys.stdout.write("\r" + prompt + "".join(buffer[:cursor_position]))
            sys.stdout.flush()
