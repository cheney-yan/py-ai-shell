"""OpenAI API interactions for py-ai-shell."""

import re
import platform
from typing import Dict, List, Any, Callable, Optional, AsyncGenerator

from openai import AsyncOpenAI

from .os_detect import detect_shell
from .error import KnownError
from .command_history import CommandResult

# Constants for prompt templates
EXPLAIN_IN_SECOND_REQUEST = True

def get_operation_system_details():
    """Get the operating system details."""
    return platform.system()

def get_shell_details():
    """Get shell details for prompts."""
    shell_details = detect_shell()
    return f"The target shell is {shell_details}"

# Prompt templates
SHELL_DETAILS = get_shell_details()

EXPLAIN_SCRIPT = """
Please provide a clear, concise description of the script, using minimal words. Outline the steps in a list format.
"""

GENERATION_DETAILS = f"""
Only reply with the single line command surrounded by three backticks. It must be able to be directly run in the target shell. Do not include any other text.

Make sure the command runs on {get_operation_system_details()} operating system.
"""

# Regular expressions for extracting code blocks
SHELL_CODE_EXCLUSIONS = [
    re.compile(r"```[a-zA-Z]*\n", re.IGNORECASE),
    re.compile(r"```[a-zA-Z]*", re.IGNORECASE),
    "\n"
]

def get_full_prompt(prompt: str, command_history: Optional[str] = None) -> str:
    """Create the full prompt for command generation."""
    command_history_section = f"""
# Recent Command History
{command_history}

Consider the above command history when generating a command.
""" if command_history else ""

    explanation_section = "" if EXPLAIN_IN_SECOND_REQUEST else EXPLAIN_SCRIPT

    return f"""
Create a single line command that one can enter in a terminal and run, based on what is specified in the prompt.

{SHELL_DETAILS}

{GENERATION_DETAILS}

{explanation_section}

{command_history_section}

The prompt is: {prompt}
"""

def get_explanation_prompt(script: str) -> str:
    """Create the prompt for command explanation."""
    return f"""
{EXPLAIN_SCRIPT}

The script: {script}
"""

def get_revision_prompt(prompt: str, code: str) -> str:
    """Create the prompt for command revision."""
    return f"""
Update the following script based on what is asked in the following prompt.

The script: {code}

The prompt: {prompt}

{GENERATION_DETAILS}
"""

def get_command_analysis_prompt(command_result: CommandResult, command_history: str, elaboration_level: int = 2, original_prompt: Optional[str] = None) -> str:
    """Create the prompt for command analysis with varying levels of elaboration.

    Args:
        command_result: The result of the failed command
        command_history: Recent command history
        elaboration_level: Level of elaboration (1-3, where 1 is minimal, 3 is detailed)
        original_prompt: The original user prompt that led to this command
    """
    original_intent = f"""
# Original Intent
My original request was: "{original_prompt}"
""" if original_prompt else ""

    # Pre-format stdout and stderr sections to avoid nested f-strings
    stdout_section = ""
    if command_result.stdout:
        stdout_section = f"STDOUT:\n{command_result.stdout}"

    stderr_section = ""
    if command_result.stderr:
        stderr_section = f"STDERR:\n{command_result.stderr}"

    # Determine the "based on" text
    based_on_text = "original intent, " if original_prompt else ""

    # Adjust instructions based on elaboration level
    if elaboration_level == 1:  # Minimal (?)
        instructions = """
1. Briefly identify the main error
2. Provide a quick fix suggestion
"""
    elif elaboration_level == 2:  # Standard (??)
        instructions = """
1. Analyze what went wrong with the current command
2. Consider the context of my previous commands to understand what I'm trying to accomplish
3. Provide specific suggestions to fix the issue
4. If appropriate, suggest an improved command that would work better
"""
    else:  # Detailed (???)
        instructions = """
1. Analyze what went wrong with the current command in detail
2. Consider the context of my previous commands to understand what I'm trying to accomplish
3. Provide specific suggestions to fix the issue with explanations
4. If appropriate, suggest an improved command that would work better
5. If there are multiple possible solutions, explain the trade-offs
6. Provide additional context or educational information about the commands or concepts involved
"""

    return f"""
I ran a shell command that failed. Please analyze the error and provide suggestions to fix it.
Adjust your response to be {["brief and concise", "moderately detailed", "comprehensive and detailed"][elaboration_level-1]}.

{original_intent}

# Current Failed Command
Command: {command_result.command}
Exit code: {command_result.exit_code}
{stdout_section}
{stderr_section}

# Recent Command History
{command_history}

Based on my {based_on_text}recent command history and the current failed command, please:

{instructions}
"""

class OpenAIClient:
    """Client for OpenAI API interactions."""

    def __init__(self, api_key: str, api_endpoint: str = "https://api.openai.com/v1"):
        """Initialize the OpenAI client."""
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=api_endpoint
        )
        self._closed = False

    async def generate_completion(self, prompt: str, model: str = "gpt-4.1-nano", number: int = 1) -> AsyncGenerator[str, None]:
        """Generate a completion from the OpenAI API."""
        if self._closed:
            raise KnownError("Client is closed")

        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                n=min(number, 10),
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            # Check for specific HTTP status codes
            error_str = str(e)

            # 401 Unauthorized - Invalid API key
            if "401" in error_str:
                raise KnownError(
                    "OpenAI API authentication failed (401 error). Your API key is invalid. "
                    f"Please check your API key and try again. Error details: {error_str}"
                )

            # 403 Forbidden - No permission, revoked key, etc.
            elif "403" in error_str:
                raise KnownError(
                    "OpenAI API access forbidden (403 error). This usually means your API key is valid but has been revoked "
                    "or doesn't have permission to access the requested resource. "
                    f"Please check your API key and try again. Error details: {error_str}"
                )

            # 429 Too Many Requests - Rate limit exceeded
            elif "429" in error_str:
                raise KnownError(
                    "OpenAI API rate limit exceeded (429 error). You've sent too many requests in a short period. "
                    "Please wait a moment before trying again. "
                    f"Error details: {error_str}"
                )

            # 500, 502, 503, 504 - Server errors
            elif any(code in error_str for code in ["500", "502", "503", "504"]):
                raise KnownError(
                    f"OpenAI API server error. The API is currently experiencing issues. "
                    f"Please try again later. Error details: {error_str}"
                )

            # Handle other API errors
            else:
                raise KnownError(f"OpenAI API request failed: {error_str}")

    async def aclose(self) -> None:
        """Close the client and release resources."""
        if not self._closed:
            try:
                await self.client.close()
            except Exception:
                # Ignore errors during closing
                pass
            finally:
                self._closed = True

    def __del__(self):
        """Destructor to ensure resources are released."""
        # This is a fallback and may not always work as expected
        # Always prefer explicit aclose() calls
        if not self._closed and hasattr(self, 'client'):
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.aclose())
            except Exception:
                # Ignore errors during cleanup
                pass

# This function is no longer used but kept for reference
# async def read_stream(stream: AsyncGenerator[str, None], callback: Callable[[str], None]) -> str:
#     """Read a stream and apply a callback to each chunk."""
#     result = ""
#     async for chunk in stream:
#         result += chunk
#         callback(chunk)
#     return result

async def extract_code(text: str, exclusions: List[Any]) -> str:
    """Extract code from text by applying exclusions."""
    result = text
    for exclusion in exclusions:
        if isinstance(exclusion, str):
            result = result.replace(exclusion, "")
        elif hasattr(exclusion, "sub"):
            result = exclusion.sub("", result)
    return result

async def get_script_and_info(prompt: str, key: str, model: str, api_endpoint: str, command_history: Optional[str] = None) -> Dict[str, Any]:
    """Get a script and its explanation from the OpenAI API."""
    full_prompt = get_full_prompt(prompt, command_history)
    client = OpenAIClient(api_key=key, api_endpoint=api_endpoint)

    try:
        stream = client.generate_completion(prompt=full_prompt, model=model)

        # Collect all chunks
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        # Join all chunks
        full_text = "".join(chunks)

        # Extract code
        code = await extract_code(full_text, SHELL_CODE_EXCLUSIONS)

        # Create read functions
        async def read_script(callback: Callable[[str], None]) -> str:
            callback(code)
            return code

        async def read_info(callback: Callable[[str], None]) -> str:
            # In this implementation, we don't have separate info
            # Call the callback with an empty string to maintain the interface
            callback("")
            return ""

        return {
            "read_script": read_script,
            "read_info": read_info
        }
    finally:
        # Ensure the client is closed
        await client.aclose()

async def get_explanation(script: str, key: str, model: str, api_endpoint: str) -> Dict[str, Any]:
    """Get an explanation for a script from the OpenAI API."""
    prompt = get_explanation_prompt(script)
    client = OpenAIClient(api_key=key, api_endpoint=api_endpoint)

    try:
        stream = client.generate_completion(prompt=prompt, model=model)

        # Collect all chunks
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        # Join all chunks
        full_text = "".join(chunks)

        # Create read function
        async def read_explanation(callback: Callable[[str], None]) -> str:
            callback(full_text)
            return full_text

        return {
            "read_explanation": read_explanation
        }
    finally:
        # Ensure the client is closed
        await client.aclose()

async def get_revision(prompt: str, code: str, key: str, model: str, api_endpoint: str) -> Dict[str, Any]:
    """Get a revised script from the OpenAI API."""
    full_prompt = get_revision_prompt(prompt, code)
    client = OpenAIClient(api_key=key, api_endpoint=api_endpoint)

    try:
        stream = client.generate_completion(prompt=full_prompt, model=model)

        # Collect all chunks
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        # Join all chunks
        full_text = "".join(chunks)

        # Extract code
        code = await extract_code(full_text, SHELL_CODE_EXCLUSIONS)

        # Create read function
        async def read_script(callback: Callable[[str], None]) -> str:
            callback(code)
            return code

        return {
            "read_script": read_script
        }
    finally:
        # Ensure the client is closed
        await client.aclose()

def get_command_summary_prompt(command_result: CommandResult, command_history: str, elaboration_level: int = 2, original_prompt: Optional[str] = None) -> str:
    """Create the prompt for command output summary.

    Args:
        command_result: The result of the successful command
        command_history: Recent command history
        elaboration_level: Level of elaboration (1-3, where 1 is minimal, 3 is detailed)
        original_prompt: The original user prompt that led to this command
    """
    original_intent = f"""
# Original Intent
My original request was: "{original_prompt}"
""" if original_prompt else ""

    # Pre-format stdout section to avoid nested f-strings
    stdout_section = ""
    if command_result.stdout:
        stdout_section = f"STDOUT:\n{command_result.stdout}"

    # Adjust instructions based on elaboration level
    if elaboration_level == 1:  # Minimal (?)
        instructions = """
1. Briefly summarize what the command did
2. Highlight the most important output
"""
    elif elaboration_level == 2:  # Standard (??)
        instructions = """
1. Summarize what the command did
2. Explain the key parts of the output
3. Provide context for understanding the results
"""
    else:  # Detailed (???)
        instructions = """
1. Provide a detailed explanation of what the command did
2. Analyze the output comprehensively
3. Explain any technical terms or concepts in the output
4. Suggest potential next steps or related commands
5. Provide educational information about the command and its output
"""

    return f"""
I ran a shell command that succeeded. Please summarize the output.
Adjust your response to be {["brief and concise", "moderately detailed", "comprehensive and detailed"][elaboration_level-1]}.

{original_intent}

# Current Successful Command
Command: {command_result.command}
{stdout_section}

# Recent Command History
{command_history}

# Instructions
{instructions}

Based on the {["command output", "command output and context", "command output, context, and original intent"][elaboration_level-1]}, provide a summary that helps me understand the results.
"""

async def get_command_summary(command_result: CommandResult, command_history: str, key: str, api_endpoint: str, model: str, elaboration_level: int = 2, original_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Get a summary of a successful command output from the OpenAI API.

    Args:
        command_result: The result of the successful command
        command_history: Recent command history
        key: OpenAI API key
        api_endpoint: OpenAI API endpoint
        model: OpenAI model to use
        elaboration_level: Level of elaboration (1-3, where 1 is minimal, 3 is detailed)
        original_prompt: The original user prompt that led to this command
    """
    prompt = get_command_summary_prompt(command_result, command_history, elaboration_level, original_prompt)
    client = OpenAIClient(api_key=key, api_endpoint=api_endpoint)

    try:
        stream = client.generate_completion(prompt=prompt, model=model)

        # Collect all chunks
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        # Join all chunks
        full_text = "".join(chunks)

        # Create read function
        async def read_summary(callback: Callable[[str], None]) -> str:
            callback(full_text)
            return full_text

        return {
            "read_summary": read_summary
        }
    finally:
        # Ensure the client is closed
        await client.aclose()

async def get_command_analysis(command_result: CommandResult, command_history: str, key: str, api_endpoint: str, model: str, elaboration_level: int = 2, original_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Get an analysis of a failed command from the OpenAI API.

    Args:
        command_result: The result of the failed command
        command_history: Recent command history
        key: OpenAI API key
        api_endpoint: OpenAI API endpoint
        model: OpenAI model to use
        elaboration_level: Level of elaboration (1-3, where 1 is minimal, 3 is detailed)
        original_prompt: The original user prompt that led to this command
    """
    prompt = get_command_analysis_prompt(command_result, command_history, elaboration_level, original_prompt)
    client = OpenAIClient(api_key=key, api_endpoint=api_endpoint)

    try:
        stream = client.generate_completion(prompt=prompt, model=model)

        # Collect all chunks
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        # Join all chunks
        full_text = "".join(chunks)

        # Create read function
        async def read_analysis(callback: Callable[[str], None]) -> str:
            callback(full_text)
            return full_text

        return {
            "read_analysis": read_analysis
        }
    finally:
        # Ensure the client is closed
        await client.aclose()
