# py-ai-shell

[![Python Package](https://github.com/cheney-yan/py-ai-shell/actions/workflows/python-package.yml/badge.svg)](https://github.com/cheney-yan/py-ai-shell/actions/workflows/python-package.yml)
[![PyPI version](https://badge.fury.io/py/py-ai-shell.svg)](https://badge.fury.io/py/py-ai-shell)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered shell assistant that generates and explains shell commands based on natural language prompts.

py-ai-shell transforms your natural language descriptions into shell commands, explains what they do, and helps you fix errors. It's like having a shell expert by your side, making command-line work more accessible and efficient.

## Installation

```bash
pip install py-ai-shell
```

**Requirements:**
- Python 3.8 or higher
- OpenAI API key

py-ai-shell works on Linux, macOS, and Windows with support for bash, zsh, fish, and PowerShell.

## Quick Start

### Basic Usage

```bash
# Start py-ai-shell interactive mode
ai

# Run with a one-time prompt
ai "list all files in the current directory"

# Configure py-ai-shell
ai config set OPENAI_KEY=your_api_key
```

When you run a command, py-ai-shell will:
1. Generate the appropriate shell command
2. Show you what it's going to do
3. Execute the command when you approve
4. Provide explanations and error analysis if needed

## Features

- **Natural Language Command Generation**: Convert plain English to shell commands
- **Command Explanations**: Understand what commands do before running them
- **Error Analysis**: Get explanations and suggestions when commands fail
- **Command History**: py-ai-shell remembers context from previous commands
- **Multiple Shell Support**: Works with bash, zsh, fish, and PowerShell
- **Interactive Mode**: Full interactive shell experience
- **One-off Mode**: Quick command generation without entering interactive mode
- **Configurable**: Use different OpenAI models and customize behavior
- **Copy to Clipboard**: Easily copy generated commands
- **Silent Mode**: Less verbose output for experienced users

## Configuration

py-ai-shell can be configured using the `config` command:

```bash
# Set your OpenAI API key
ai config set OPENAI_KEY=your_api_key

# Set the model to use (default: gpt-4.1-nano)
ai config set MODEL=gpt-4.1-nano

# Enable silent mode (less verbose output)
ai config set SILENT_MODE=true

# Set API endpoint (useful for proxies or alternative providers)
ai config set OPENAI_API_ENDPOINT=https://api.openai.com/v1

# Set language (default: en)
ai config set LANGUAGE=en
```

Configuration is stored in `~/.config/py-ai-shell/config.ini` and can be edited directly.

## Advanced Usage

### Command Options

```bash
# Run in silent mode (less verbose output)
ai -s "list files by size"

# Provide a custom prompt
ai -p "show disk usage"
```

### Error Analysis

When a command fails, py-ai-shell can analyze the error and suggest fixes:

```bash
$ ai "find files modified in the last 24 hours"
# If the command fails, py-ai-shell will offer to analyze the error
Command failed. Would you like an explanation? (?/??/???)
```

Enter `?` for a brief explanation, `??` for a standard explanation, or `???` for a detailed analysis.

### Command History

py-ai-shell maintains a history of your recent commands and their results, providing context for future commands. This helps the AI understand your environment and previous actions.

### Interactive Options

After a command is generated, you'll see options:
- `a/A`: Accept and run the command
- `e/E`: Edit the command before running
- `r/R`: Revise (ask AI to generate a new command)
- `c/C`: Copy the command to clipboard
- `s/S`: Stick to your original command
- `q/Q`: Quit/cancel

### Using with Different Shells

py-ai-shell automatically detects your current shell, but you can generate commands for specific shells by mentioning them in your prompt:

```bash
ai "list all processes in PowerShell syntax"
```

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/cheney-yan/py-ai-shell.git
   cd py-ai-shell
   ```

2. Install development dependencies:
   ```bash
   make dev
   ```

3. Run tests:
   ```bash
   make test
   ```

### Available Make Commands

- `make help`: Show available commands
- `make clean`: Remove all build, test, coverage and Python artifacts
- `make lint`: Check style with flake8
- `make test`: Run tests
- `make coverage`: Check code coverage
- `make dist`: Package for distribution
- `make install`: Install the package locally
- `make dev`: Install development dependencies

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure your code passes all tests and linting checks before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- This project is inspired by the [AI Shell project](https://github.com/BuilderIO/ai-shell)
- Built with [OpenAI API](https://openai.com/api/)
- Command-line interface powered by [Click](https://click.palletsprojects.com/)
- Terminal styling with [Rich](https://rich.readthedocs.io/)
