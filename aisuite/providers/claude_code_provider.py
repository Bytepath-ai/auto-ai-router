"""Claude Code Provider for aisuite

This provider implements support for Claude Code, which runs via the terminal command.
Claude Code is a local CLI tool for software engineering tasks.
"""

import subprocess
from typing import Dict, List, Any, Optional
from aisuite.framework import ChatCompletionResponse
from aisuite.framework.provider_interface import ProviderInterface
from aisuite.framework.message import Message
from aisuite.framework.choice import Choice


class Claude_codeProvider(ProviderInterface):
    """Provider for Claude Code via terminal execution"""
    
    def __init__(self, **config):
        """Initialize the Claude Code provider
        
        Args:
            **config: Configuration options (currently unused for Claude Code)
        """
        self.config = config
    
    def chat_completions_create(self, model: str, messages: List[Message], **kwargs) -> ChatCompletionResponse:
        """Create a chat completion using Claude Code
        
        Args:
            model: Model name (ignored for Claude Code as it only has one model)
            messages: List of messages in the conversation
            **kwargs: Additional arguments (ignored for Claude Code)
            
        Returns:
            ChatCompletionResponse object containing Claude Code's response
        """
        # Extract the last user message
        user_prompt = ""
        for msg in reversed(messages):
            # Handle both dict and Message object formats
            if isinstance(msg, dict):
                if msg.get("role") == "user":
                    user_prompt = msg.get("content", "")
                    break
            else:
                if msg.role == "user":
                    user_prompt = msg.content
                    break
        
        if not user_prompt:
            raise ValueError("No user message found in the conversation")
        
        # Call Claude Code via terminal
        response_content = self._call_claude_code(user_prompt)
        
        # Create response in the expected format
        choice = Choice()
        choice.message = Message(role="assistant", content=response_content)
        choice.finish_reason = "stop"
        
        response = ChatCompletionResponse()
        response.choices = [choice]
        
        return response
    
    def _call_claude_code(self, prompt: str) -> str:
        """Execute Claude Code via terminal and return the response
        
        Args:
            prompt: The prompt to send to Claude Code
            
        Returns:
            The response from Claude Code
        """
        try:
            import os
            # Get the playground directory in the current working directory
            playground_dir = os.path.join(os.getcwd(), 'playground')
            
            # Ensure the playground directory exists
            if not os.path.exists(playground_dir):
                os.makedirs(playground_dir)
            
            # Execute claude command with the prompt in the playground directory
            result = subprocess.run(
                ['claude', '--dangerously-skip-permissions', '-p', prompt],
                capture_output=True,
                text=True,
                check=False,
                cwd=playground_dir  # Set working directory to playground
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return f"Error calling Claude Code: {error_msg}"
        except FileNotFoundError:
            return "Error: Claude Code CLI not found. Please ensure 'claude' is installed and in PATH."
        except Exception as e:
            return f"Error calling Claude Code: {str(e)}"