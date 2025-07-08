#!/usr/bin/env python3
"""
Intelligent AI Model Router using aisuite

This router uses GPT-4o to analyze prompts and automatically determine 
the best model to use (GPT-4o vs Claude) based on the prompt characteristics.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import aisuite as ai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class ModelProfile:
    """Profile for each model with its strengths and characteristics"""
    name: str
    provider: str
    model_id: str
    strengths: List[str]
    cost_per_1k_tokens: float  # Average of input/output costs
    

class AIRouter:
    """Intelligent router that uses GPT-4o to determine the best model for a given prompt"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the router with configuration"""
        self.client = ai.Client()
        
        # Configure providers if config provided
        if config:
            self.client.configure(config)
        
        # Define model profiles
        self.models = {
            "gpt-4o": ModelProfile(
                name="GPT-4o",
                provider="openai",
                model_id="gpt-4o",
                strengths=[
                    "general knowledge",
                    "reasoning",
                    "mathematics",
                    "data analysis",
                    "structured output",
                    "function calling",
                    "vision capabilities",
                    "fast response time"
                ],
                cost_per_1k_tokens=0.00375  # ($2.50 input + $5.00 output) / 2
            ),
            "claude": ModelProfile(
                name="Claude 3.5 Sonnet",
                provider="anthropic",
                model_id="claude-3-5-sonnet-20241022",
                strengths=[
                    "creative writing",
                    "code generation",
                    "complex reasoning",
                    "nuanced understanding",
                    "ethical considerations",
                    "detailed explanations",
                    "context retention",
                    "long-form content"
                ],
                cost_per_1k_tokens=0.009  # ($3 input + $15 output) / 2
            )
        }
        
        # Router model (always GPT-4o for fast, consistent routing decisions)
        self.router_model = "openai:gpt-4o"
    
    def _create_routing_prompt(self, user_prompt: str) -> str:
        """Create the prompt for the routing decision"""
        return f"""You are an AI model router. Analyze the following user prompt and determine which model would be best suited to handle it.

Available models:
1. GPT-4o: {', '.join(self.models['gpt-4o'].strengths)}
2. Claude 3.5 Sonnet: {', '.join(self.models['claude'].strengths)}

User prompt:
"{user_prompt}"

Respond with ONLY a JSON object in this exact format:
{{
    "model": "gpt-4o" or "claude",
    "reasoning": "Brief explanation of why this model is best for this prompt",
    "confidence": 0.0 to 1.0
}}

Consider:
- Task complexity and type
- Required capabilities
- Length of expected response
- Need for creativity vs precision
"""
    
    def _parse_routing_decision(self, response: str) -> Tuple[str, str, float]:
        """Parse the routing decision from GPT-4o response"""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                decision = json.loads(json_str)
                return (
                    decision.get("model", "gpt-4o"),
                    decision.get("reasoning", ""),
                    decision.get("confidence", 0.8)
                )
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Default to GPT-4o if parsing fails
        return "gpt-4o", "Failed to parse routing decision", 0.5
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze a prompt and determine the best model to use"""
        routing_prompt = self._create_routing_prompt(prompt)
        
        # Get routing decision from GPT-4o
        response = self.client.chat.completions.create(
            model=self.router_model,
            messages=[{"role": "user", "content": routing_prompt}],
            temperature=0.1,  # Low temperature for consistent routing
            max_tokens=200
        )
        
        model_choice, reasoning, confidence = self._parse_routing_decision(
            response.choices[0].message.content
        )
        
        # Get the selected model profile
        selected_profile = self.models[model_choice]
        
        return {
            "selected_model": model_choice,
            "model_id": f"{selected_profile.provider}:{selected_profile.model_id}",
            "reasoning": reasoning,
            "confidence": confidence,
            "estimated_cost_per_1k": selected_profile.cost_per_1k_tokens
        }
    
    def route(self, 
             messages: List[Dict[str, str]], 
             **kwargs) -> Any:
        """Route a request to the appropriate model"""
        # Extract the user's prompt from messages
        user_prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_prompt = msg.get("content", "")
                break
        
        # Analyze and select model
        analysis = self.analyze_prompt(user_prompt)
        selected_model_id = analysis["model_id"]
        
        # Log routing decision
        print(f"Routing to: {analysis['selected_model']} (confidence: {analysis['confidence']:.2f})")
        print(f"Reasoning: {analysis['reasoning']}")
        
        # Forward request to selected model
        return self.client.chat.completions.create(
            model=selected_model_id,
            messages=messages,
            **kwargs
        )
    
    def route_with_metadata(self, 
                           messages: List[Dict[str, str]], 
                           **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """Route a request and return both the response and routing metadata"""
        # Extract the user's prompt
        user_prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_prompt = msg.get("content", "")
                break
        
        # Analyze and select model
        analysis = self.analyze_prompt(user_prompt)
        selected_model_id = analysis["model_id"]
        
        # Forward request to selected model
        response = self.client.chat.completions.create(
            model=selected_model_id,
            messages=messages,
            **kwargs
        )
        
        return response, analysis


def main():
    """Example usage of the AI Router"""
    # Initialize router with API keys
    router = AIRouter({
        "openai": {"api_key": os.getenv("OPENAI_API_KEY")},
        "anthropic": {"api_key": os.getenv("ANTHROPIC_API_KEY")}
    })
    
    # Example prompts to test routing
    test_prompts = [
        "Write a creative short story about a robot learning to paint",
        "Calculate the derivative of f(x) = 3x^2 + 2x - 5",
        "Generate a Python function to sort a list of dictionaries",
        "Explain quantum computing in simple terms",
        "Analyze the ethical implications of AI in healthcare",
        "What's the weather like today?",
        "Help me debug this React component that's not rendering"
    ]
    
    print("AI Router Demo\n" + "="*50 + "\n")
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        print("-" * 50)
        
        # Get routing decision and send to selected model
        messages = [{"role": "user", "content": prompt}]
        
        try:
            # Route the request and get both response and metadata
            response, metadata = router.route_with_metadata(
                messages=messages,
                temperature=0.7,
                max_tokens=150  # Limit for demo purposes
            )
            
            # Display routing information
            print(f"Selected Model: {metadata['selected_model']}")
            print(f"Reasoning: {metadata['reasoning']}")
            print(f"Confidence: {metadata['confidence']:.2f}")
            print(f"\nModel Response:")
            print(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("=" * 50)


if __name__ == "__main__":
    main()