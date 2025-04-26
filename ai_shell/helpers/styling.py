"""Styling helpers for AI Shell."""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich.padding import Padding
from rich.syntax import Syntax

# Create a console for rich output
console = Console()

def print_header(text, style="blue"):
    """Print a section header with color.

    Args:
        text: The header text to display
        style: The color to use for the header
    """
    # Get the console width
    width = console.width

    # Create the header with a line
    header = f"─── {text} " + "─" * (width - len(text) - 5)

    # Print the header
    console.print(header, style=f"bold {style}")

def print_content(content, markdown=False):
    """Print content with proper indentation.

    Args:
        content: The content to display
        markdown: Whether to render the content as markdown
    """
    if markdown:
        # For markdown content, we need to handle it differently
        md = Markdown(content)
        # Add left padding for indentation
        padded_content = Padding(md, (0, 2, 0, 2))
        console.print(padded_content)
    else:
        # For plain text, add indentation
        indented_content = Text(content)
        padded_content = Padding(indented_content, (0, 2, 0, 2))
        console.print(padded_content)

def print_script_section(title, script, style="blue"):
    """Print a script section with header and content as markdown with bash syntax highlighting.

    Args:
        title: The section title
        script: The script content
        style: The color to use for the header
    """
    # Get the console width
    width = console.width

    # Create the top border with the title
    top_border = f"─── {title} " + "─" * (width - len(title) - 5)

    # Print the header
    console.print(top_border, style=f"bold {style}")

    # Format as markdown code block if it's not already
    if not (script.startswith("```") and script.endswith("```")):
        markdown_script = f"```bash\n{script}\n```"
    else:
        markdown_script = script

    # Print the content with markdown formatting
    console.print(Markdown(markdown_script))

def print_explanation_section(title, explanation, style="blue"):
    """Print an explanation section with header and markdown content.

    Args:
        title: The section title
        explanation: The explanation content (markdown)
        style: The color to use for the header
    """
    # Get the console width
    width = console.width

    # Create the top border with the title
    top_border = f"─── {title} " + "─" * (width - len(title) - 5)

    # Print the header
    console.print(top_border, style=f"bold {style}")

    # Create a markdown object with the explanation
    md = Markdown(explanation)

    # Print the markdown content
    console.print(md)

def print_options_section(title, style="blue"):
    """Print an options section with header and options using single-letter shortcuts.

    Args:
        title: The section title
        style: The color to use for the header
    """
    # Get the console width
    width = console.width

    # Create the top border with the title
    top_border = f"─── {title} " + "─" * (width - len(title) - 5)

    # Display options with single-letter shortcuts on a single line
    options_text = (
        "[bright_green]a/A: Accept[/bright_green] | "
        "[yellow]e/E: Edit[/yellow] | "
        "[yellow]r/R: Revise[/yellow] | "
        "[cyan]s/S: Stick to mine[/cyan] | "
        "[bright_blue]c/C: Copy[/bright_blue] | "
        "[bright_red]q/Q: Quit[/bright_red]"
    )

    # Print the header and options
    console.print(top_border, style=f"bold {style}")
    console.print(options_text)

def print_welcome_banner(text):
    """Print a welcome banner with the text in the middle and double lines extending to both ends.

    Args:
        text: The welcome text
    """
    # Get the console width
    width = console.width

    # Add padding around the text
    padded_text = f" {text} "

    # Calculate the length of the double lines on each side
    line_length = (width - len(padded_text)) // 2

    # Create the double lines
    double_line = "═" * line_length

    # Create the full banner with text in the middle and double lines on both sides
    banner = f"{double_line}{padded_text}{double_line}"

    # If the banner is shorter than the console width (due to odd numbers), add one more character
    if len(banner) < width:
        banner += "═"

    # Print the banner with blue color
    console.print(banner, style="bold blue")

def print_command_output(output_text, style="orange1"):
    """Print command output with bash syntax highlighting using Rich's Syntax class.

    Args:
        output_text: The command output text
        style: The color to use for the header
    """
    # Get the console width
    width = console.width

    # Create the top border with the title
    title = "Command output:"
    top_border = f"─── {title} " + "─" * (width - len(title) - 5)

    # Print the header
    console.print(top_border, style=f"bold {style}")

    # Check if the output is empty or just the "No output" message
    if not output_text.strip() or output_text.strip() == "[italic]No output[/italic]":
        console.print(output_text)
        return

    # Check if the output contains stderr
    if "__STDERR__" in output_text:
        # Split the output into stdout and stderr parts
        parts = output_text.split("__STDERR__")

        # Print stdout part with markdown if it exists
        if parts[0].strip():
            # Format as markdown code block if it's not already
            stdout_text = parts[0].strip()
            if not (stdout_text.startswith("```") and stdout_text.endswith("```")):
                stdout_text = f"```bash\n{stdout_text}\n```"
            console.print(Markdown(stdout_text))

        # Print stderr part with the red header and markdown
        if len(parts) > 1 and parts[1].strip():
            console.print("\n[bold red]STDERR:[/bold red]")
            # Format as markdown code block if it's not already
            stderr_text = parts[1].strip()
            if not (stderr_text.startswith("```") and stderr_text.endswith("```")):
                stderr_text = f"```bash\n{stderr_text}\n```"
            console.print(Markdown(stderr_text))
    else:
        # Format as markdown code block if it's not already
        if not (output_text.startswith("```") and output_text.endswith("```")) and output_text.strip() and output_text.strip() != "[italic]No output[/italic]":
            output_text = f"```bash\n{output_text}\n```"
        console.print(Markdown(output_text))

def print_error(text):
    """Print an error message.

    Args:
        text: The error message
    """
    error_text = Text(f"❌ {text}")
    error_text.stylize("bold red")
    console.print(error_text)

def print_success(text):
    """Print a success message.

    Args:
        text: The success message
    """
    success_text = Text(f"✅ {text}")
    success_text.stylize("bold green")
    console.print(success_text)
