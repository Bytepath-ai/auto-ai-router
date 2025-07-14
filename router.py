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
from datetime import datetime
import threading

# Load environment variables from .env file
load_dotenv()

ROUTING_PROMPT_TEMPLATE = """You are an AI model router. Analyze the following user prompt and determine which model would be best suited to handle it.

Available models:
1. Claude Code: {claude_code_strengths}
2. Claude Opus 4: {claude_opus_strengths}
3. O3: {o3_strengths}
4. GPT-4o: {gpt4o_strengths}
5. GPT-4o-mini: {gpt4o_mini_strengths}
6. Grok-4: {grok4_strengths}

{historical_stats}

User prompt:
"{user_prompt}"

Respond with ONLY a JSON object in this exact format:
{{
    "model": "claude-code" or "claude-opus" or "o3" or "gpt-4o" or "gpt-4o-mini" or "grok-4",
    "reasoning": "Brief explanation of why this model is best for this prompt",
    "confidence": 0.0 to 1.0
}}

Consider:
- Task complexity and type
- Required capabilities
- Length of expected response
- Need for creativity vs precision
- Historical performance data for similar tasks
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

TASK_CATEGORIZATION_PROMPT = """Analyze the following user prompt and generate a concise task name (3-8 words) that captures the essence of what is being requested.

User prompt: "{user_prompt}"

Respond with ONLY a JSON object in this exact format:
{{
    "task_name": "concise descriptive name of the task",
    "task_category": "for example one of: coding, reasoning, general, creative, analysis, simple"
}}"""

RESPONSE_SCORING_PROMPT = """Score the following AI model responses to a user prompt. Each response should be scored on a scale of 1-10.

User prompt: "{user_prompt}"

Responses:
{responses}

Scoring criteria:
- Accuracy and correctness (0-2 points)
- Completeness and depth (0-2 points)
- Clarity and coherence (0-2 points)
- Relevance to the prompt (0-2 points)
- Helpfulness to the user (0-2 points)

Respond with ONLY a JSON object in this exact format:
{{
    "scores": {{
        "model_name_1": score_1_to_10,
        "model_name_2": score_2_to_10,
        ...
    }},
    "brief_reasoning": "1-2 sentence explanation of the scoring"
}}"""

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
        # Load historical statistics
        stats = self._load_statistics()
        
        # Format historical statistics for the prompt
        historical_stats_text = ""
        if stats:
            historical_stats_text = "Historical performance data:\n"
            for category, model_counts in stats.items():
                if model_counts:
                    best_model = max(model_counts.items(), key=lambda x: x[1])
                    historical_stats_text += f"- {category} tasks: {best_model[0]} performed best ({best_model[1]} times)\n"
            historical_stats_text = historical_stats_text.strip()
        else:
            historical_stats_text = "No historical performance data available yet."
        
        return ROUTING_PROMPT_TEMPLATE.format(
            claude_code_strengths=', '.join(self.models['claude-code'].strengths),
            claude_opus_strengths=', '.join(self.models['claude-opus'].strengths),
            o3_strengths=', '.join(self.models['o3'].strengths),
            gpt4o_strengths=', '.join(self.models['gpt-4o'].strengths),
            gpt4o_mini_strengths=', '.join(self.models['gpt-4o-mini'].strengths),
            grok4_strengths=', '.join(self.models['grok-4'].strengths),
            historical_stats=historical_stats_text,
            user_prompt=user_prompt
        )
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, stats_file: str = "parallel_route_stats.txt"):
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
            ),
            "grok-4": ModelProfile(
                name="Grok-4",
                provider="xai",
                model_id="grok-4-0709",
                strengths=[
                    "real-time information",
                    "current events analysis",
                    "social media understanding",
                    "humor and wit",
                    "conversational responses",
                    "technical explanations",
                    "creative writing",
                    "contextual understanding"
                ],
                cost_per_1k_tokens=0.01  # Estimated cost
            )
        }
        
        # Router model (always GPT-4o for fast, consistent routing decisions)
        self.router_model = "openai:gpt-4o"
        
        # Statistics tracking
        self.stats_file = stats_file
        self.stats_lock = threading.Lock()
    
    def _transform_kwargs_for_model(self, model_id: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Transform kwargs based on model requirements"""
        # Create a copy to avoid modifying the original
        transformed_kwargs = kwargs.copy()
        
        # Special handling for o3 model
        if "o3" in model_id and "max_tokens" in transformed_kwargs:
            # o3 requires max_completion_tokens instead of max_tokens
            transformed_kwargs["max_completion_tokens"] = transformed_kwargs.pop("max_tokens")
        
        return transformed_kwargs
    
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
            temperature=0.1  # Low temperature for consistent routing
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
        
        # Transform kwargs for the selected model
        transformed_kwargs = self._transform_kwargs_for_model(selected_model_id, kwargs)
        
        # Forward request to selected model
        return self.client.chat.completions.create(
            model=selected_model_id,
            messages=messages,
            **transformed_kwargs
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
        
        # Transform kwargs for the selected model
        transformed_kwargs = self._transform_kwargs_for_model(selected_model_id, kwargs)
        
        # Forward request to selected model
        response = self.client.chat.completions.create(
            model=selected_model_id,
            messages=messages,
            **transformed_kwargs
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
                
                # Transform kwargs for the specific model
                transformed_kwargs = self._transform_kwargs_for_model(model_id, kwargs)
                
                # Call models via aisuite
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    **transformed_kwargs
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
        
        # Categorize the task
        task_info = self._categorize_task(user_prompt)
        
        # Score the responses
        scoring_result = self._score_responses(user_prompt, responses)
        
        # Evaluate responses using GPT-4o
        evaluation = self._evaluate_responses(user_prompt, responses)
        
        # Find the best response
        best_model_key = evaluation["best_model"]
        best_response = next(r for r in responses if r["model_name"] == best_model_key)
        
        # Prepare statistics data
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'task_name': task_info['task_name'],
            'task_category': task_info['task_category'],
            'user_prompt': user_prompt[:500],  # Limit prompt length for CSV
            'claude_code_score': scoring_result['scores'].get('Claude Code', 0),
            'claude_opus_score': scoring_result['scores'].get('Claude Opus 4', 0),
            'o3_score': scoring_result['scores'].get('O3', 0),
            'gpt4o_score': scoring_result['scores'].get('GPT-4o', 0),
            'gpt4o_mini_score': scoring_result['scores'].get('GPT-4o-mini', 0),
            'grok4_score': scoring_result['scores'].get('Grok-4', 0),
            'best_model': best_model_key,
            'scoring_reasoning': scoring_result.get('brief_reasoning', ''),
            'evaluation_reasoning': evaluation.get('reasoning', '')
        }
        
        # Save statistics
        self._save_statistics(stats_data)
        
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
            "task_info": task_info,
            "scoring": scoring_result,
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
                
                # Transform kwargs for the specific model
                transformed_kwargs = self._transform_kwargs_for_model(model_id, kwargs)
                
                # Call models via aisuite
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    **transformed_kwargs
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
        
        # Categorize the task
        task_info = self._categorize_task(user_prompt)
        
        # Score the responses
        scoring_result = self._score_responses(user_prompt, responses)
        
        # Evaluate responses to determine the best individual model
        evaluation = self._evaluate_responses(user_prompt, responses)
        
        # Find the best model based on evaluation
        best_model_name = evaluation["best_model"]
        
        # Prepare statistics data
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'task_name': task_info['task_name'],
            'task_category': task_info['task_category'],
            'user_prompt': user_prompt[:500],  # Limit prompt length for CSV
            'claude_code_score': scoring_result['scores'].get('Claude Code', 0),
            'claude_opus_score': scoring_result['scores'].get('Claude Opus 4', 0),
            'o3_score': scoring_result['scores'].get('O3', 0),
            'gpt4o_score': scoring_result['scores'].get('GPT-4o', 0),
            'gpt4o_mini_score': scoring_result['scores'].get('GPT-4o-mini', 0),
            'grok4_score': scoring_result['scores'].get('Grok-4', 0),
            'best_model': best_model_name,
            'scoring_reasoning': scoring_result.get('brief_reasoning', ''),
            'evaluation_reasoning': evaluation.get('reasoning', '')
        }
        
        # Save statistics
        self._save_statistics(stats_data)
        
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
            "models_used": [r["model_name"] for r in responses],
            "task_info": task_info,
            "scoring": scoring_result,
            "evaluation": evaluation,
            "best_individual_model": best_model_name
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
            temperature=0.1
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
            temperature=0.3  # Slightly higher than evaluation for more creative synthesis
        )
        
        return synth_response.choices[0].message.content
    
    def _categorize_task(self, user_prompt: str) -> Dict[str, str]:
        """Use GPT-4o to categorize the task and generate a task name"""
        categorization_prompt = TASK_CATEGORIZATION_PROMPT.format(user_prompt=user_prompt)
        
        response = self.client.chat.completions.create(
            model=self.router_model,
            messages=[{"role": "user", "content": categorization_prompt}],
            temperature=0.1
        )
        
        try:
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Default if parsing fails
        return {
            "task_name": "Unknown Task",
            "task_category": "general"
        }
    
    def _score_responses(self, user_prompt: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use GPT-4o to score model responses"""
        # Format responses for scoring
        formatted_responses = "\n\n".join([
            f"Model: {r['model_name']}\nResponse: {r['response']}"
            for r in responses
        ])
        
        scoring_prompt = RESPONSE_SCORING_PROMPT.format(
            user_prompt=user_prompt,
            responses=formatted_responses
        )
        
        response = self.client.chat.completions.create(
            model=self.router_model,
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0.1
        )
        
        try:
            content = response.choices[0].message.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Default scores if parsing fails
        default_scores = {r['model_name']: 5 for r in responses}
        return {
            "scores": default_scores,
            "brief_reasoning": "Failed to parse scoring response"
        }
    
    def _save_statistics(self, stats_data: Dict[str, Any]):
        """Save statistics to file with proper locking"""
        with self.stats_lock:
            with open(self.stats_file, 'a', encoding='utf-8') as f:
                # Save only task_category and best_model
                f.write(f"{stats_data['task_category']},{stats_data['best_model']}\n")
    
    def _load_statistics(self) -> Dict[str, Dict[str, int]]:
        """Load and parse statistics from file"""
        stats = {}
        try:
            with self.stats_lock:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and ',' in line:
                            category, model = line.split(',', 1)
                            if category not in stats:
                                stats[category] = {}
                            if model not in stats[category]:
                                stats[category][model] = 0
                            stats[category][model] += 1
        except FileNotFoundError:
            # File doesn't exist yet, return empty stats
            pass
        except Exception as e:
            print(f"Warning: Error loading statistics: {e}")
        
        return stats

