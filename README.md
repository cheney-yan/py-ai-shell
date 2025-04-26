# AI Shell (Python Version)

AI-powered shell assistant that generates and explains shell commands based on natural language prompts.

## Installation

```bash
pip install ai-shell
```

## Usage

```bash
# Start AI Shell
ai

# Run with a prompt
ai "list all files in the current directory"

# Configure AI Shell
ai config set OPENAI_KEY=your_api_key
```

## Features

- Generate shell commands from natural language prompts
- Explain what commands do
- Analyze failed commands and suggest fixes
- Track command history for context
- Support for multiple shells (bash, zsh, fish, PowerShell)
- Configurable API endpoints and models

## Configuration

You can configure AI Shell using the `config` command:

```bash
# Set your OpenAI API key
ai config set OPENAI_KEY=your_api_key

# Set the model to use
ai config set MODEL=gpt-4o-mini

# Enable silent mode (less verbose output)
ai config set SILENT_MODE=true
```

## License

MIT
