"""Prompt handling and command execution for py-ai-shell."""

import sys
import time
import asyncio
import subprocess
import threading
from typing import Optional

from rich.prompt import Prompt
from rich.live import Live
from rich.markdown import Markdown

from .helpers.config import get_config
from .helpers.constants import PROJECT_NAME
from .helpers.completion import (
    get_script_and_info,
    get_explanation,
    get_revision,
    get_command_analysis,
    get_command_summary
)
from .helpers.command_history import (
    CommandResult,
    add_to_command_history,
    format_command_history_for_ai
)
from .helpers.shell_history import append_to_shell_history
from .helpers.styling import (
    console,
    print_header,
    print_script_section,
    print_explanation_section,
    print_options_section,
    print_welcome_banner,
    print_error,
    print_success
)

# Global state for AI interaction
in_ai_interaction = False

async def run_script(script: str, key: str, model: str, api_endpoint: str, original_prompt: Optional[str] = None) -> int:
    """Run a shell script and capture its output."""
    # Import and use the in_command_execution flag from cli.py
    # Use importlib to avoid circular import issues
    import importlib
    cli_module = importlib.import_module(f"{__package__}.cli")

    try:
        # Display a running indicator with colored header
        print_script_section("Running command:", script, style="bright_green")

        # Set the flag to indicate we're in a command execution
        cli_module.in_command_execution = True

        # Set up the output section header
        width = console.width
        title = "Command output:"
        top_border = f"─── {title} " + "─" * (width - len(title) - 5)
        console.print(top_border, style="bold orange3")

        # Initialize variables to collect output
        stdout_content = []
        stderr_content = []

        try:
            # Execute command with pipe instead of inherit to capture output
            process = subprocess.Popen(
                script,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )

            # Create a live display for streaming output
            with Live("```bash\n```", refresh_per_second=4, console=console) as live:
                # Define functions to stream output
                def stream_stdout():
                    for line in iter(process.stdout.readline, ''):
                        stdout_content.append(line)
                        # Update the live display
                        display_content = f"```bash\n{''.join(stdout_content)}"
                        if stderr_content:
                            display_content += f"\n\nSTDERR:\n{''.join(stderr_content)}"
                        display_content += "\n```"
                        live.update(Markdown(display_content))

                def stream_stderr():
                    for line in iter(process.stderr.readline, ''):
                        stderr_content.append(line)
                        # Update the live display
                        display_content = f"```bash\n{''.join(stdout_content)}"
                        if stderr_content:
                            display_content += f"\n\nSTDERR:\n{''.join(stderr_content)}"
                        display_content += "\n```"
                        live.update(Markdown(display_content))

                # Create threads to stream stdout and stderr
                stdout_thread = threading.Thread(target=stream_stdout)
                stderr_thread = threading.Thread(target=stream_stderr)

                # Set threads as daemon so they exit when the main thread exits
                stdout_thread.daemon = True
                stderr_thread.daemon = True

                # Start the threads
                stdout_thread.start()
                stderr_thread.start()

                # Wait for the process to complete
                while process.poll() is None:
                    await asyncio.sleep(0.1)

                # Process has completed, wait a bit for threads to finish processing output
                await asyncio.sleep(0.2)

            # Get the exit code and output
            exit_code = process.returncode
            stdout = ''.join(stdout_content)
            stderr = ''.join(stderr_content)
        except KeyboardInterrupt:
            # If the user presses Ctrl+C during command execution,
            # terminate the process and set appropriate values
            process.terminate()
            try:
                process.wait(timeout=2)  # Give it a chance to terminate gracefully
            except:
                process.kill()  # Force kill if it doesn't terminate

            stdout = "Command was cancelled by user."
            stderr = ""
            exit_code = 130  # Standard exit code for SIGINT

            console.print("\nCommand cancelled.", style="yellow")
        finally:
            # Always reset the flag, even if there's an exception
            cli_module.in_command_execution = False

        # Format the output for final display
        output_text = ""
        stdout_text = stdout.strip() if stdout else ""
        stderr_text = stderr.strip() if stderr else ""

        # Pass the raw output text and let styling.py handle the markdown formatting
        if stdout_text:
            output_text += stdout_text

        if stderr_text:
            if output_text:
                output_text += "\n\n"
            # Add a marker for stderr that styling.py can recognize
            output_text += f"__STDERR__\n{stderr_text}"

        if not output_text:
            output_text = "[italic]No output[/italic]"

        # Show status
        if exit_code == 0:
            print_success("Command completed successfully")
        elif exit_code == 130:  # SIGINT (Ctrl+C)
            console.print("Command was cancelled by user", style="yellow")
        else:
            print_error(f"Command failed with exit code {exit_code}")

        # Store command in history
        command_result = CommandResult(
            command=script,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            timestamp=time.time()
        )

        add_to_command_history(command_result)
        append_to_shell_history(script)

        # Define elaboration levels mapping
        elaboration_levels = {
            "?": 1,    # Minimal explanation/summary
            "??": 2,   # Standard explanation/summary
            "???": 3   # Detailed explanation/summary
        }

        # If command failed (but wasn't cancelled) and we have API credentials, ask if user wants an analysis
        if exit_code != 0 and exit_code != 130 and key and api_endpoint:
            # Prompt the user to choose an elaboration level
            console.print("\nCommand failed. Would you like an explanation?", style="yellow")
            explanation_choice = Prompt.ask(
                "Explain a bit more? (?/??/???)",
                choices=["", "?", "??", "???"],
                default=""
            )

            # If the user wants an explanation, analyze the failure
            if explanation_choice in elaboration_levels:
                await analyze_failed_command(
                    command_result,
                    key,
                    api_endpoint,
                    model,
                    elaboration_levels[explanation_choice],
                    original_prompt
                )
        # If command succeeded and we have API credentials, ask if user wants a summary
        elif exit_code == 0 and key and api_endpoint and stdout.strip():
            # Prompt the user to choose an elaboration level
            console.print("\nCommand succeeded. Would you like a summary?", style="green")
            summary_choice = Prompt.ask(
                "Do you want a summary (?/??/???)",
                choices=["", "?", "??", "???"],
                default=""
            )

            # If the user wants a summary, analyze the successful command
            if summary_choice in elaboration_levels:
                await analyze_successful_command(
                    command_result,
                    key,
                    api_endpoint,
                    model,
                    elaboration_levels[summary_choice],
                    original_prompt
                )

        return exit_code
    except Exception as e:
        # This should only happen for errors in executing the command itself, not command failures
        print_header("Error executing command:", style="red")
        print_error(str(e))
        return 1

async def analyze_failed_command(command_result: CommandResult, key: str, api_endpoint: str, model: str, elaboration_level: int = 2, original_prompt: Optional[str] = None) -> None:
    """Analyze a failed command and provide suggestions.

    Args:
        command_result: The result of the failed command
        key: OpenAI API key
        api_endpoint: OpenAI API endpoint
        model: OpenAI model to use
        elaboration_level: Level of elaboration (1-3, where 1 is minimal, 3 is detailed)
        original_prompt: The original user prompt that led to this command
    """
    # Map elaboration level to a descriptive status message
    status_messages = {
        1: "Providing quick analysis...",
        2: "Analyzing error...",
        3: "Performing detailed analysis..."
    }

    with console.status(status_messages.get(elaboration_level, "Analyzing error..."), spinner="dots"):
        try:
            command_history = format_command_history_for_ai()
            analysis_result = await get_command_analysis(
                command_result=command_result,
                command_history=command_history,
                key=key,
                api_endpoint=api_endpoint,
                model=model,
                elaboration_level=elaboration_level,
                original_prompt=original_prompt
            )

            # Capture the analysis
            analysis_content = []
            await analysis_result["read_analysis"](lambda text: analysis_content.append(text))
            analysis_text = "".join(analysis_content)

            # Display the analysis with a colored header and markdown content
            # Adjust the header based on elaboration level
            headers = {
                1: "Quick error fix:",
                2: "Error analysis:",
                3: "Detailed error analysis:"
            }
            print_explanation_section(headers.get(elaboration_level, "Error analysis:"), analysis_text, style="bright_yellow")
        except Exception as e:
            print_header("Error analysis failed", style="red")
            print_error(str(e))

async def analyze_successful_command(command_result: CommandResult, key: str, api_endpoint: str, model: str, elaboration_level: int = 2, original_prompt: Optional[str] = None) -> None:
    """Analyze a successful command and provide a summary.

    Args:
        command_result: The result of the successful command
        key: OpenAI API key
        api_endpoint: OpenAI API endpoint
        model: OpenAI model to use
        elaboration_level: Level of elaboration (1-3, where 1 is minimal, 3 is detailed)
        original_prompt: The original user prompt that led to this command
    """
    # Map elaboration level to a descriptive status message
    status_messages = {
        1: "Providing brief summary...",
        2: "Summarizing output...",
        3: "Creating detailed summary..."
    }

    with console.status(status_messages.get(elaboration_level, "Summarizing output..."), spinner="dots"):
        try:
            command_history = format_command_history_for_ai()
            summary_result = await get_command_summary(
                command_result=command_result,
                command_history=command_history,
                key=key,
                api_endpoint=api_endpoint,
                model=model,
                elaboration_level=elaboration_level,
                original_prompt=original_prompt
            )

            # Capture the summary
            summary_content = []
            await summary_result["read_summary"](lambda text: summary_content.append(text))
            summary_text = "".join(summary_content)

            # Display the summary with a colored header and markdown content
            # Adjust the header based on elaboration level
            headers = {
                1: "Quick summary:",
                2: "Command summary:",
                3: "Detailed summary:"
            }
            print_explanation_section(headers.get(elaboration_level, "Command summary:"), summary_text, style="bright_green")
        except Exception as e:
            print_header("Summary generation failed", style="red")
            print_error(str(e))

async def get_prompt(prompt: Optional[str] = None) -> str:
    """Get a prompt from the user."""
    if prompt:
        return prompt
    try:
        # Remove the style parameter as it's not supported by Prompt.ask()
        return Prompt.ask("What would you like me to do?", default="Which folder I am at?")
    except (KeyboardInterrupt, EOFError):
        # If user presses Ctrl+D, raise ExitShellException to exit the shell
        from .helpers.error import ExitShellException
        console.print("\nExiting py-ai-shell. Goodbye!", style="cyan")
        raise ExitShellException("User requested exit with Ctrl+D")

async def run_or_revise_flow(script: str, key: str, model: str, api_endpoint: str, silent_mode: bool, original_prompt: str) -> None:
    """Flow for running or revising a script."""
    empty_script = not script.strip()

    if empty_script:
        console.print("No command was generated. Let's try again.", style="yellow")
        return

    # Display options with a colored header and bullet points
    print_options_section("What to do?", style="orange1")

    # Ask the user what to do with single-letter shortcuts
    choice = Prompt.ask(
        "",
        choices=["a", "e", "r", "s", "c", "q", "A", "E", "R", "S", "C", "Q"],
        default="a"
    ).lower()

    if choice == "a":  # Accept/Run
        await run_script(script, key, model, api_endpoint, original_prompt)
    elif choice == "e":  # Edit
        # Clear some space for better visibility
        console.print("\n")

        # Display instructions for editing
        console.print("Edit the script below. Use standard editing keys (arrows, backspace, delete, etc.)", style="yellow")
        console.print("Press Enter when done or Ctrl+C to cancel.", style="yellow")

        try:
            # Import our custom editor
            from .helpers.editor import edit

            # Use the editor to edit the script
            # This provides a full-featured line editor with cursor movement,
            # history, and other editing capabilities
            new_script = edit(prompt="", default=script)

            # Display the edited script
            console.print("\nYour edited script:", style="green")
            print_script_section("Your edited script:", new_script, style="orange1")

            # Run the edited script
            await run_script(new_script, key, model, api_endpoint, original_prompt)
        except KeyboardInterrupt:
            # Handle cancellation
            console.print("\nEdit cancelled. Returning to options.", style="yellow")
            # Return to the options menu
            await run_or_revise_flow(script, key, model, api_endpoint, silent_mode, original_prompt)
    elif choice == "r":  # Revise
        await revise_script(original_prompt, script, key, model, api_endpoint, silent_mode)
    elif choice == "s":  # Stick to mine (run user's original command)
        # Use the original prompt as the command
        user_command = original_prompt.strip()

        # Display the user's original command
        console.print("\nRunning your original command:", style="cyan")
        print_script_section("Your command:", user_command, style="cyan")

        # Run the user's original command
        await run_script(user_command, key, model, api_endpoint, original_prompt)
    elif choice == "c":  # Copy
        import pyperclip
        pyperclip.copy(script)
        console.print("Script copied to clipboard!", style="green")
    elif choice == "q":  # Quit
        console.print("Goodbye!", style="cyan")
        sys.exit(0)

async def revise_script(prompt: str, script: str, key: str, model: str, api_endpoint: str, silent_mode: bool) -> None:
    """Revise a script based on user feedback."""
    feedback = Prompt.ask("What would you like to change about the script?")

    with console.status("Revising script...", spinner="dots"):
        revision_result = await get_revision(
            prompt=f"{prompt}\n\nFeedback: {feedback}",
            code=script,
            key=key,
            model=model,
            api_endpoint=api_endpoint
        )

    # Capture the revised script
    script_content = []
    new_script = await revision_result["read_script"](lambda text: script_content.append(text))
    script_text = "".join(script_content)

    # Display the revised script with a colored header and indented content
    print_script_section("Your new script:", script_text, style="orange1")

    if not silent_mode:
        with console.status("Getting explanation...", spinner="dots"):
            explanation_result = await get_explanation(
                script=new_script,
                key=key,
                model=model,
                api_endpoint=api_endpoint
            )

        # Capture the explanation
        explanation_content = []
        await explanation_result["read_explanation"](lambda text: explanation_content.append(text))
        explanation_text = "".join(explanation_content)

        # Display the explanation with a colored header and markdown content
        print_explanation_section("Explanation:", explanation_text, style="bright_blue")

    await run_or_revise_flow(new_script, key, model, api_endpoint, silent_mode, prompt)

async def prompt(use_prompt: Optional[str] = None, silent_mode: bool = False) -> None:
    """Main prompt function."""
    global in_ai_interaction

    # Import ExitShellException at the top level
    from .helpers.error import ExitShellException

    # Get configuration - this will exit immediately if API key is missing
    # We don't catch SystemExit here to allow the program to exit
    config = get_config()
    key = config["OPENAI_KEY"]
    api_endpoint = config["OPENAI_API_ENDPOINT"]
    model = config["MODEL"]
    silent_mode = silent_mode or config["SILENT_MODE"].lower() == "true"

    # Display a welcome banner
    print_welcome_banner(f"Welcome to {PROJECT_NAME}")

    # Set the global flag to indicate we're in an AI interaction
    in_ai_interaction = True

    try:
        # This might raise ExitShellException, which we want to propagate up
        the_prompt = await get_prompt(use_prompt)

        with console.status("Loading...", spinner="dots"):
            command_history = format_command_history_for_ai()
            script_result = await get_script_and_info(
                prompt=the_prompt,
                key=key,
                model=model,
                api_endpoint=api_endpoint,
                command_history=command_history
            )

        # Capture the script
        script_content = []
        script = await script_result["read_script"](lambda text: script_content.append(text))
        script_text = "".join(script_content)

        # Display the script with a colored header and indented content
        print_script_section("Suggested script:", script_text, style="blue")

        if not silent_mode:
            with console.status("Getting explanation...", spinner="dots"):
                info = await script_result["read_info"](lambda _: None)

                if not info:
                    explanation_result = await get_explanation(
                        script=script,
                        key=key,
                        model=model,
                        api_endpoint=api_endpoint
                    )

                    # Capture the explanation
                    explanation_content = []
                    await explanation_result["read_explanation"](lambda text: explanation_content.append(text))
                    explanation_text = "".join(explanation_content)

                    # Display the explanation with a colored header and markdown content
                    print_explanation_section("Explanation:", explanation_text, style="bright_blue")

        await run_or_revise_flow(script, key, model, api_endpoint, silent_mode, the_prompt)
    except ExitShellException:
        # Let ExitShellException propagate up to the CLI handler
        raise
    except Exception as e:
        # Print the error message
        print_error(str(e))
        # Re-raise KnownError exceptions to ensure they're handled properly by the CLI
        from .helpers.error import KnownError
        if isinstance(e, KnownError):
            raise
    finally:
        # Reset the global flag
        in_ai_interaction = False
