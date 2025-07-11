#!/usr/bin/env python3
"""
Intelligent AI Model Router using aisuite

This router uses GPT-4o to analyze prompts and automatically determine 
the best model to use based on the prompt characteristics:
- Claude Code: For coding tasks that need to be applied in repo
- Claude Opus 4: For coding responses without applying in repo
- O3: For complex reasoning tasks
- GPT-4o: For general/overall tasks
- GPT-4o-mini: For simple quick queries
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import aisuite as ai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

ROUTING_PROMPT_TEMPLATE = """You are an AI model router. Analyze the following user prompt and determine which model would be best suited to handle it.

Available models:
1. Claude Code: {claude_code_strengths}
2. Claude Opus 4: {claude_opus_strengths}
3. O3: {o3_strengths}
4. GPT-4o: {gpt4o_strengths}
5. GPT-4o-mini: {gpt4o_mini_strengths}

User prompt:
"{user_prompt}"

Respond with ONLY a JSON object in this exact format:
{{
    "model": "claude-code" or "claude-opus" or "o3" or "gpt-4o" or "gpt-4o-mini",
    "reasoning": "Brief explanation of why this model is best for this prompt",
    "confidence": 0.0 to 1.0
}}

Consider:
- Task complexity and type
- Required capabilities
- Length of expected response
- Need for creativity vs precision
"""

EVALUATION_PROMPT_TEMPLATE = """You are an AI response evaluator. Given a user prompt and multiple AI model responses, determine which response is the best.

User prompt: "{user_prompt}"

Responses:
{responses}

Evaluate the responses based on:
- Accuracy and correctness
- Completeness and depth
- Clarity and coherence
- Relevance to the prompt
- Helpfulness to the user

Respond with ONLY a JSON object in this exact format:
{{
    "best_model": "model name that provided the best response",
    "reasoning": "Brief explanation of why this response is best",
    "ranking": ["first_model", "second_model", ...] // ranked from best to worst
}}"""

SYNTHESIS_PROMPT_TEMPLATE = """You are an AI response synthesizer. Given a user prompt and multiple AI model responses, create a comprehensive synthesis that combines the best elements from all responses.

User prompt: "{user_prompt}"

Responses:
{responses}

Create a synthesized response that:
- Combines the strengths and unique insights from each model
- Eliminates redundancy while preserving important details
- Maintains coherence and natural flow
- Incorporates the best explanations, examples, and approaches from all responses
- Preserves any unique valuable contributions from individual models

Provide ONLY the synthesized response, without any meta-commentary about the synthesis process."""

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
    
    def _create_routing_prompt(self, user_prompt: str) -> str:
        """Create the prompt for the routing decision"""
        return ROUTING_PROMPT_TEMPLATE.format(
            claude_code_strengths=', '.join(self.models['claude-code'].strengths),
            claude_opus_strengths=', '.join(self.models['claude-opus'].strengths),
            o3_strengths=', '.join(self.models['o3'].strengths),
            gpt4o_strengths=', '.join(self.models['gpt-4o'].strengths),
            gpt4o_mini_strengths=', '.join(self.models['gpt-4o-mini'].strengths),
            user_prompt=user_prompt
        )
    
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
            "claude-opus": ModelProfile(
                name="Claude Opus 4",
                provider="anthropic",
                model_id="claude-opus-4-20250514",
                strengths=[
                    "code generation",
                    "programming solutions",
                    "algorithm design",
                    "code explanation",
                    "technical documentation",
                    "code review",
                    "debugging assistance",
                    "API design"
                ],
                cost_per_1k_tokens=0.015  # Estimated cost
            ),
            "o3": ModelProfile(
                name="O3",
                provider="openai",
                model_id="o3",
                strengths=[
                    "complex reasoning",
                    "mathematical proofs",
                    "logical analysis",
                    "problem solving",
                    "strategic thinking",
                    "scientific reasoning",
                    "multi-step reasoning",
                    "abstract thinking"
                ],
                cost_per_1k_tokens=0.020  # Estimated cost
            ),
            "gpt-4o-mini": ModelProfile(
                name="GPT-4o-mini",
                provider="openai",
                model_id="gpt-4o-mini",
                strengths=[
                    "quick responses",
                    "simple queries",
                    "basic information",
                    "lightweight tasks",
                    "cost efficiency",
                    "fast processing",
                    "straightforward answers",
                    "basic explanations"
                ],
                cost_per_1k_tokens=0.00015  # ($0.15 input + $0.60 output) / 2000
            ),
            "claude-code": ModelProfile(
                name="Claude Code",
                provider="claude_code",
                model_id="claude",
                strengths=[
                    "in repo software engineering",
                    "in repo code implementation",
                    "in repo debugging",
                    "in repo file system operations",
                    "in repo bash commands",
                    "in repo project structure understanding",
                    "in repo refactoring",
                    "in repo test writing",
                    "in repo technical documentation",
                    "in repo CLI tool development"
                ],
                cost_per_1k_tokens=0.0  # Free when running locally
            )
        }
        
        # Router model (always GPT-4o for fast, consistent routing decisions)
        self.router_model = "openai:gpt-4o"
    
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
    
    def parallelbest_route(self, 
                      messages: List[Dict[str, str]], 
                      **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """Call all models in parallel and return the best response"""
        import concurrent.futures
        
        # Extract user prompt
        user_prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_prompt = msg.get("content", "")
                break
        
        # Function to call a model and return its response
        def call_model(model_key: str, model_profile: ModelProfile):
            try:
                model_id = f"{model_profile.provider}:{model_profile.model_id}"
                
                # Call models via aisuite
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    **kwargs
                )
                return {
                    "model_key": model_key,
                    "model_name": model_profile.name,
                    "response": response.choices[0].message.content,
                    "model_id": model_id,
                    "cost_per_1k": model_profile.cost_per_1k_tokens
                }
            except Exception as e:
                return {
                    "model_key": model_key,
                    "model_name": model_profile.name,
                    "response": f"Error: {str(e)}",
                    "model_id": model_id,
                    "cost_per_1k": model_profile.cost_per_1k_tokens,
                    "error": True
                }
        
        # Call all models in parallel
        responses = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.models)) as executor:
            future_to_model = {
                executor.submit(call_model, key, profile): key 
                for key, profile in self.models.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_model):
                result = future.result()
                if not result.get("error", False):
                    responses.append(result)
        
        # If no successful responses, return an error
        if not responses:
            raise Exception("All models failed to generate responses")
        
        # Evaluate responses using GPT-4o
        evaluation = self._evaluate_responses(user_prompt, responses)
        
        # Find the best response
        best_model_key = evaluation["best_model"]
        best_response = next(r for r in responses if r["model_name"] == best_model_key)
        
        # Create a response object matching the expected format
        class MockResponse:
            class Choice:
                class Message:
                    def __init__(self, content):
                        self.content = content
                
                def __init__(self, content):
                    self.message = self.Message(content)
            
            def __init__(self, content):
                self.choices = [self.Choice(content)]
        
        return MockResponse(best_response["response"]), {
            "selected_model": best_response["model_key"],
            "model_id": best_response["model_id"],
            "evaluation": evaluation,
            "all_responses": responses,
            "parallelbest_mode": True
        }
    
    def parallelsynthetize_route(self, 
                                messages: List[Dict[str, str]], 
                                **kwargs) -> Tuple[Any, Dict[str, Any]]:
        """Call all models in parallel and synthesize their responses into one comprehensive answer"""
        import concurrent.futures
        
        # Extract user prompt
        user_prompt = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_prompt = msg.get("content", "")
                break
        
        # Function to call a model and return its response
        def call_model(model_key: str, model_profile: ModelProfile):
            try:
                model_id = f"{model_profile.provider}:{model_profile.model_id}"
                
                # Call models via aisuite
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    **kwargs
                )
                return {
                    "model_key": model_key,
                    "model_name": model_profile.name,
                    "response": response.choices[0].message.content,
                    "model_id": model_id,
                    "cost_per_1k": model_profile.cost_per_1k_tokens
                }
            except Exception as e:
                return {
                    "model_key": model_key,
                    "model_name": model_profile.name,
                    "response": f"Error: {str(e)}",
                    "model_id": model_id,
                    "cost_per_1k": model_profile.cost_per_1k_tokens,
                    "error": True
                }
        
        # Call all models in parallel
        responses = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.models)) as executor:
            future_to_model = {
                executor.submit(call_model, key, profile): key 
                for key, profile in self.models.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_model):
                result = future.result()
                if not result.get("error", False):
                    responses.append(result)
        
        # If no successful responses, return an error
        if not responses:
            raise Exception("All models failed to generate responses")
        
        # Synthesize responses using GPT-4o
        synthesized_response = self._synthesize_responses(user_prompt, responses)
        
        # Create a response object matching the expected format
        class MockResponse:
            class Choice:
                class Message:
                    def __init__(self, content):
                        self.content = content
                
                def __init__(self, content):
                    self.message = self.Message(content)
            
            def __init__(self, content):
                self.choices = [self.Choice(content)]
        
        return MockResponse(synthesized_response), {
            "synthesis_mode": True,
            "parallelsynthetize_mode": True,
            "all_responses": responses,
            "models_used": [r["model_name"] for r in responses]
        }
    
    def _evaluate_responses(self, user_prompt: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use GPT-4o to evaluate multiple responses and select the best one"""
        # Format responses for evaluation
        formatted_responses = "\n\n".join([
            f"Model: {r['model_name']}\nResponse: {r['response']}"
            for r in responses
        ])
        
        evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt,
            responses=formatted_responses
        )
        
        # Get evaluation from GPT-4o
        eval_response = self.client.chat.completions.create(
            model=self.router_model,
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.1,
            max_tokens=300
        )
        
        # Parse evaluation response
        try:
            eval_content = eval_response.choices[0].message.content
            start = eval_content.find('{')
            end = eval_content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = eval_content[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Default to first response if parsing fails
        return {
            "best_model": responses[0]["model_name"],
            "reasoning": "Failed to parse evaluation",
            "ranking": [r["model_name"] for r in responses]
        }
    
    def _synthesize_responses(self, user_prompt: str, responses: List[Dict[str, Any]]) -> str:
        """Use GPT-4o to synthesize multiple responses into a comprehensive answer"""
        # Format responses for synthesis
        formatted_responses = "\n\n".join([
            f"Model: {r['model_name']}\nResponse: {r['response']}"
            for r in responses
        ])
        
        synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
            user_prompt=user_prompt,
            responses=formatted_responses
        )
        
        # Get synthesis from GPT-4o
        synth_response = self.client.chat.completions.create(
            model=self.router_model,
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.3,  # Slightly higher than evaluation for more creative synthesis
            max_tokens=2000  # Allow for longer synthesized responses
        )
        
        return synth_response.choices[0].message.content

