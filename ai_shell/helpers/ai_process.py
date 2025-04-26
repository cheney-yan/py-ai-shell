"""Separate process for AI API calls to allow for Ctrl+C interruption."""

import sys
import json
import asyncio
import multiprocessing
import time
from typing import Dict, Any, Optional

from openai import AsyncOpenAI

# Global variable to store the process
ai_process = None

def start_ai_process():
    """Start the AI process."""
    global ai_process
    if ai_process is None or not ai_process.is_alive():
        ai_process = multiprocessing.Process(target=ai_process_main)
        ai_process.daemon = True
        ai_process.start()
    return ai_process

def kill_ai_process():
    """Kill the AI process."""
    global ai_process
    if ai_process is not None and ai_process.is_alive():
        ai_process.terminate()
        ai_process = None

def ai_process_main():
    """Main function for the AI process."""
    print("AI process started")
    
    # Set up queues for communication
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    
    # Start the event loop
    asyncio.run(ai_process_loop(input_queue, output_queue))

async def ai_process_loop(input_queue, output_queue):
    """Event loop for the AI process."""
    while True:
        # Check for messages from the main process
        if not input_queue.empty():
            message = input_queue.get()
            
            if message["type"] == "generate":
                try:
                    # Initialize OpenAI client
                    client = AsyncOpenAI(
                        api_key=message["key"],
                        base_url=message["api_endpoint"]
                    )
                    
                    # Generate the completion
                    stream = await client.chat.completions.create(
                        model=message.get("model", "gpt-4.1-nano"),
                        messages=[{"role": "user", "content": message["prompt"]}],
                        n=min(message.get("number", 1), 10),
                        stream=True
                    )
                    
                    # Process the stream and send chunks back to the main process
                    async for chunk in stream:
                        if chunk.choices and chunk.choices[0].delta.content:
                            output_queue.put({
                                "type": "chunk",
                                "data": chunk.choices[0].delta.content
                            })
                    
                    # Signal that we're done
                    output_queue.put({
                        "type": "done"
                    })
                except Exception as e:
                    # Send the error back to the main process
                    output_queue.put({
                        "type": "error",
                        "error": {
                            "message": str(e),
                            "type": type(e).__name__
                        }
                    })
        
        # Sleep to avoid busy waiting
        await asyncio.sleep(0.01)

class AIProcessClient:
    """Client for interacting with the AI process."""
    
    def __init__(self):
        """Initialize the AI process client."""
        # Start the AI process
        self.process = start_ai_process()
        
        # Set up queues for communication
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
    
    async def generate_completion(self, prompt: str, key: str, api_endpoint: str, model: Optional[str] = None, number: int = 1) -> str:
        """Generate a completion using the AI process."""
        # Send the generate message to the AI process
        self.input_queue.put({
            "type": "generate",
            "prompt": prompt,
            "key": key,
            "api_endpoint": api_endpoint,
            "model": model,
            "number": number
        })
        
        # Wait for the response
        chunks = []
        while True:
            if not self.output_queue.empty():
                message = self.output_queue.get()
                
                if message["type"] == "chunk":
                    chunks.append(message["data"])
                elif message["type"] == "done":
                    break
                elif message["type"] == "error":
                    raise Exception(message["error"]["message"])
            
            # Sleep to avoid busy waiting
            await asyncio.sleep(0.01)
        
        return "".join(chunks)
