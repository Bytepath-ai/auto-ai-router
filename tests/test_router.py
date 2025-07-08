"""Tests for the AI Router module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router import AIRouter, ModelProfile, ROUTING_PROMPT_TEMPLATE, EVALUATION_PROMPT_TEMPLATE, SYNTHESIS_PROMPT_TEMPLATE


class TestModelProfile:
    """Test the ModelProfile dataclass"""
    
    def test_model_profile_creation(self):
        """Test creating a ModelProfile instance"""
        profile = ModelProfile(
            name="Test Model",
            provider="test_provider",
            model_id="test-model-id",
            strengths=["strength1", "strength2"],
            cost_per_1k_tokens=0.001
        )
        
        assert profile.name == "Test Model"
        assert profile.provider == "test_provider"
        assert profile.model_id == "test-model-id"
        assert profile.strengths == ["strength1", "strength2"]
        assert profile.cost_per_1k_tokens == 0.001


class TestAIRouter:
    """Test the AIRouter class"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock aisuite client"""
        with patch('router.ai.Client') as mock:
            yield mock.return_value
    
    @pytest.fixture
    def router(self, mock_client):
        """Create an AIRouter instance with mocked client"""
        return AIRouter()
    
    def test_init_without_config(self, mock_client):
        """Test AIRouter initialization without config"""
        router = AIRouter()
        
        # Check that all models are properly initialized
        assert len(router.models) == 5
        assert "gpt-4o" in router.models
        assert "claude-opus" in router.models
        assert "o3" in router.models
        assert "gpt-4o-mini" in router.models
        assert "claude-code" in router.models
        
        # Check router model is set
        assert router.router_model == "openai:gpt-4o"
        
        # Verify client was created
        assert router.client == mock_client
    
    def test_init_with_config(self, mock_client):
        """Test AIRouter initialization with config"""
        config = {"test": "config"}
        router = AIRouter(config=config)
        
        # Verify config was passed to client
        mock_client.configure.assert_called_once_with(config)
    
    def test_create_routing_prompt(self, router):
        """Test routing prompt creation"""
        user_prompt = "Write a function to calculate fibonacci"
        prompt = router._create_routing_prompt(user_prompt)
        
        # Verify prompt contains user prompt
        assert user_prompt in prompt
        
        # Verify all model strengths are included
        for model_key, profile in router.models.items():
            for strength in profile.strengths:
                assert strength in prompt
    
    def test_parse_routing_decision_valid_json(self, router):
        """Test parsing valid routing decision"""
        response = '''
        Some text before
        {
            "model": "claude-opus",
            "reasoning": "This is a coding task",
            "confidence": 0.95
        }
        Some text after
        '''
        
        model, reasoning, confidence = router._parse_routing_decision(response)
        
        assert model == "claude-opus"
        assert reasoning == "This is a coding task"
        assert confidence == 0.95
    
    def test_parse_routing_decision_invalid_json(self, router):
        """Test parsing invalid routing decision"""
        response = "This is not valid JSON"
        
        model, reasoning, confidence = router._parse_routing_decision(response)
        
        # Should return defaults
        assert model == "gpt-4o"
        assert reasoning == "Failed to parse routing decision"
        assert confidence == 0.5
    
    def test_parse_routing_decision_missing_fields(self, router):
        """Test parsing routing decision with missing fields"""
        response = '{"model": "o3"}'
        
        model, reasoning, confidence = router._parse_routing_decision(response)
        
        assert model == "o3"
        assert reasoning == ""
        assert confidence == 0.8
    
    def test_analyze_prompt(self, router, mock_client):
        """Test analyze_prompt method"""
        # Mock the response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "model": "claude-code",
            "reasoning": "In-repo coding task",
            "confidence": 0.9
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        result = router.analyze_prompt("Fix the bug in main.py")
        
        assert result["selected_model"] == "claude-code"
        assert result["model_id"] == "claude_code:claude"
        assert result["reasoning"] == "In-repo coding task"
        assert result["confidence"] == 0.9
        assert result["estimated_cost_per_1k"] == 0.0
        
        # Verify correct call to client
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "openai:gpt-4o"
        assert call_args[1]["temperature"] == 0.1
        assert call_args[1]["max_tokens"] == 200
    
    def test_route(self, router, mock_client):
        """Test route method"""
        # Mock analyze response
        mock_routing_response = Mock()
        mock_routing_response.choices = [Mock()]
        mock_routing_response.choices[0].message.content = '''
        {
            "model": "gpt-4o-mini",
            "reasoning": "Simple query",
            "confidence": 0.85
        }
        '''
        
        # Mock actual model response
        mock_model_response = Mock()
        mock_model_response.choices = [Mock()]
        mock_model_response.choices[0].message.content = "42"
        
        mock_client.chat.completions.create.side_effect = [
            mock_routing_response,
            mock_model_response
        ]
        
        messages = [{"role": "user", "content": "What is 2+2?"}]
        result = router.route(messages, temperature=0.5)
        
        assert result == mock_model_response
        
        # Verify two calls were made
        assert mock_client.chat.completions.create.call_count == 2
        
        # Second call should be to the selected model
        second_call = mock_client.chat.completions.create.call_args_list[1]
        assert second_call[1]["model"] == "openai:gpt-4o-mini"
        assert second_call[1]["messages"] == messages
        assert second_call[1]["temperature"] == 0.5
    
    def test_route_with_metadata(self, router, mock_client):
        """Test route_with_metadata method"""
        # Mock responses
        mock_routing_response = Mock()
        mock_routing_response.choices = [Mock()]
        mock_routing_response.choices[0].message.content = '''
        {
            "model": "o3",
            "reasoning": "Complex reasoning task",
            "confidence": 0.92
        }
        '''
        
        mock_model_response = Mock()
        mock_client.chat.completions.create.side_effect = [
            mock_routing_response,
            mock_model_response
        ]
        
        messages = [{"role": "user", "content": "Solve this complex problem"}]
        response, metadata = router.route_with_metadata(messages)
        
        assert response == mock_model_response
        assert metadata["selected_model"] == "o3"
        assert metadata["model_id"] == "openai:o3"
        assert metadata["reasoning"] == "Complex reasoning task"
        assert metadata["confidence"] == 0.92
    
    def test_route_no_user_message(self, router, mock_client):
        """Test routing with no user message"""
        messages = [{"role": "system", "content": "You are helpful"}]
        
        # Mock routing response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "model": "gpt-4o",
            "reasoning": "Default for no user prompt",
            "confidence": 0.5
        }
        '''
        
        # Mock model response
        mock_model_response = Mock()
        mock_client.chat.completions.create.side_effect = [
            mock_response,
            mock_model_response
        ]
        
        # Should still work but with empty prompt
        router.route(messages)
        
        # Verify routing was attempted
        assert mock_client.chat.completions.create.called
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_parallelbest_route(self, mock_executor, router, mock_client):
        """Test parallelbest_route method"""
        # Mock executor behavior
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Create mock futures
        futures = []
        for model_key, profile in router.models.items():
            future = Mock()
            future.result.return_value = {
                "model_key": model_key,
                "model_name": profile.name,
                "response": f"Response from {profile.name}",
                "model_id": f"{profile.provider}:{profile.model_id}",
                "cost_per_1k": profile.cost_per_1k_tokens
            }
            futures.append(future)
        
        # Mock as_completed to return futures
        with patch('concurrent.futures.as_completed', return_value=futures):
            # Mock evaluation response
            mock_eval_response = Mock()
            mock_eval_response.choices = [Mock()]
            mock_eval_response.choices[0].message.content = '''
            {
                "best_model": "Claude Opus 4",
                "reasoning": "Best response quality",
                "ranking": ["Claude Opus 4", "O3", "GPT-4o", "Claude Code", "GPT-4o-mini"]
            }
            '''
            mock_client.chat.completions.create.return_value = mock_eval_response
            
            messages = [{"role": "user", "content": "Test prompt"}]
            response, metadata = router.parallelbest_route(messages)
            
            # Verify response content
            assert response.choices[0].message.content == "Response from Claude Opus 4"
            
            # Verify metadata
            assert metadata["selected_model"] == "claude-opus"
            assert metadata["parallelbest_mode"] is True
            assert "evaluation" in metadata
            assert "all_responses" in metadata
            assert len(metadata["all_responses"]) == 5
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_parallelsynthetize_route(self, mock_executor, router, mock_client):
        """Test parallelsynthetize_route method"""
        # Mock executor behavior
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Create mock futures
        futures = []
        for model_key, profile in router.models.items():
            future = Mock()
            future.result.return_value = {
                "model_key": model_key,
                "model_name": profile.name,
                "response": f"Response from {profile.name}",
                "model_id": f"{profile.provider}:{profile.model_id}",
                "cost_per_1k": profile.cost_per_1k_tokens
            }
            futures.append(future)
        
        # Mock as_completed to return futures
        with patch('concurrent.futures.as_completed', return_value=futures):
            # Mock synthesis response
            mock_synth_response = Mock()
            mock_synth_response.choices = [Mock()]
            mock_synth_response.choices[0].message.content = "Synthesized response combining all models"
            mock_client.chat.completions.create.return_value = mock_synth_response
            
            messages = [{"role": "user", "content": "Test prompt"}]
            response, metadata = router.parallelsynthetize_route(messages)
            
            # Verify response content
            assert response.choices[0].message.content == "Synthesized response combining all models"
            
            # Verify metadata
            assert metadata["synthesis_mode"] is True
            assert metadata["parallelsynthetize_mode"] is True
            assert "all_responses" in metadata
            assert "models_used" in metadata
            assert len(metadata["models_used"]) == 5
    
    def test_evaluate_responses(self, router, mock_client):
        """Test _evaluate_responses helper method"""
        responses = [
            {"model_name": "GPT-4o", "response": "Response 1"},
            {"model_name": "Claude Opus 4", "response": "Response 2"}
        ]
        
        # Mock evaluation response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "best_model": "Claude Opus 4",
            "reasoning": "More comprehensive",
            "ranking": ["Claude Opus 4", "GPT-4o"]
        }
        '''
        mock_client.chat.completions.create.return_value = mock_response
        
        result = router._evaluate_responses("Test prompt", responses)
        
        assert result["best_model"] == "Claude Opus 4"
        assert result["reasoning"] == "More comprehensive"
        assert result["ranking"] == ["Claude Opus 4", "GPT-4o"]
        
        # Verify correct prompt was used
        call_args = mock_client.chat.completions.create.call_args
        assert "Test prompt" in call_args[1]["messages"][0]["content"]
        assert "GPT-4o" in call_args[1]["messages"][0]["content"]
        assert "Claude Opus 4" in call_args[1]["messages"][0]["content"]
    
    def test_evaluate_responses_parse_failure(self, router, mock_client):
        """Test _evaluate_responses with parse failure"""
        responses = [
            {"model_name": "Model1", "response": "Response 1"},
            {"model_name": "Model2", "response": "Response 2"}
        ]
        
        # Mock invalid response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Invalid JSON"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = router._evaluate_responses("Test prompt", responses)
        
        # Should return defaults
        assert result["best_model"] == "Model1"
        assert result["reasoning"] == "Failed to parse evaluation"
        assert result["ranking"] == ["Model1", "Model2"]
    
    def test_synthesize_responses(self, router, mock_client):
        """Test _synthesize_responses helper method"""
        responses = [
            {"model_name": "GPT-4o", "response": "Response 1"},
            {"model_name": "Claude Opus 4", "response": "Response 2"}
        ]
        
        # Mock synthesis response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Combined synthesized response"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = router._synthesize_responses("Test prompt", responses)
        
        assert result == "Combined synthesized response"
        
        # Verify synthesis call
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["temperature"] == 0.3
        assert call_args[1]["max_tokens"] == 2000
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_parallel_route_with_errors(self, mock_executor, router, mock_client):
        """Test parallel routing when some models fail"""
        # Mock executor behavior
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Create mix of successful and failed futures
        futures = []
        for i, (model_key, profile) in enumerate(router.models.items()):
            future = Mock()
            if i % 2 == 0:  # Make every other model fail
                future.result.return_value = {
                    "model_key": model_key,
                    "model_name": profile.name,
                    "response": f"Error: Connection failed",
                    "model_id": f"{profile.provider}:{profile.model_id}",
                    "cost_per_1k": profile.cost_per_1k_tokens,
                    "error": True
                }
            else:
                future.result.return_value = {
                    "model_key": model_key,
                    "model_name": profile.name,
                    "response": f"Response from {profile.name}",
                    "model_id": f"{profile.provider}:{profile.model_id}",
                    "cost_per_1k": profile.cost_per_1k_tokens
                }
            futures.append(future)
        
        # Mock as_completed to return futures
        with patch('concurrent.futures.as_completed', return_value=futures):
            # Mock evaluation response
            mock_eval_response = Mock()
            mock_eval_response.choices = [Mock()]
            mock_eval_response.choices[0].message.content = '''
            {
                "best_model": "Claude Opus 4",
                "reasoning": "Best available response",
                "ranking": ["Claude Opus 4", "GPT-4o-mini"]
            }
            '''
            mock_client.chat.completions.create.return_value = mock_eval_response
            
            messages = [{"role": "user", "content": "Test prompt"}]
            response, metadata = router.parallelbest_route(messages)
            
            # Should still work with partial results
            assert response.choices[0].message.content == "Response from Claude Opus 4"
            # Only successful responses should be in all_responses
            assert len(metadata["all_responses"]) == 2  # Only successful responses
    
    @patch('concurrent.futures.ThreadPoolExecutor')
    def test_parallel_route_all_fail(self, mock_executor, router, mock_client):
        """Test parallel routing when all models fail"""
        # Mock executor behavior
        mock_executor_instance = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_executor_instance
        
        # Create all failed futures
        futures = []
        for model_key, profile in router.models.items():
            future = Mock()
            future.result.return_value = {
                "model_key": model_key,
                "model_name": profile.name,
                "response": f"Error: Connection failed",
                "model_id": f"{profile.provider}:{profile.model_id}",
                "cost_per_1k": profile.cost_per_1k_tokens,
                "error": True
            }
            futures.append(future)
        
        # Mock as_completed to return futures
        with patch('concurrent.futures.as_completed', return_value=futures):
            messages = [{"role": "user", "content": "Test prompt"}]
            
            # Should raise exception when all fail
            with pytest.raises(Exception, match="All models failed to generate responses"):
                router.parallelbest_route(messages)


class TestPromptTemplates:
    """Test the prompt templates"""
    
    def test_routing_prompt_template(self):
        """Test that routing prompt template has all required placeholders"""
        required_placeholders = [
            "claude_code_strengths",
            "claude_opus_strengths",
            "o3_strengths",
            "gpt4o_strengths",
            "gpt4o_mini_strengths",
            "user_prompt"
        ]
        
        for placeholder in required_placeholders:
            assert f"{{{placeholder}}}" in ROUTING_PROMPT_TEMPLATE
    
    def test_evaluation_prompt_template(self):
        """Test that evaluation prompt template has all required placeholders"""
        required_placeholders = ["user_prompt", "responses"]
        
        for placeholder in required_placeholders:
            assert f"{{{placeholder}}}" in EVALUATION_PROMPT_TEMPLATE
    
    def test_synthesis_prompt_template(self):
        """Test that synthesis prompt template has all required placeholders"""
        required_placeholders = ["user_prompt", "responses"]
        
        for placeholder in required_placeholders:
            assert f"{{{placeholder}}}" in SYNTHESIS_PROMPT_TEMPLATE


@pytest.mark.integration
class TestAIRouterIntegration:
    """Integration tests for AIRouter (requires API keys)"""
    
    def test_real_routing_decision(self):
        """Test with real API calls"""
        router = AIRouter()
        
        # Test various prompts
        test_prompts = [
            "Write a Python function to calculate fibonacci in fibonacci.py",
            "How are you?",
            "List all cities in Europe.",
            "Prove that sqrt(2) is irrational",
            "Write a Python function to calculate fibonacci in fibonacci.py in the current repo"
        ]
        
        for prompt in test_prompts:
            # First test analyze_prompt
            result = router.analyze_prompt(prompt)
            print(f"\nPrompt: {prompt}")
            print(f"Selected: {result['selected_model']}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Confidence: {result['confidence']}")
            
            assert result['selected_model'] in router.models
            assert 0 <= result['confidence'] <= 1
            assert result['reasoning']
            
            # Now actually call the model through route method
            messages = [{"role": "user", "content": prompt}]
            try:
                response = router.route(messages, max_tokens=50)  # Limit tokens to save API costs
                actual_response = response.choices[0].message.content
                print(f"Model Response Preview: {actual_response[:100]}...")
                
                # Verify we got a response
                assert actual_response
                assert len(actual_response) > 0
            except Exception as e:
                print(f"Error calling {result['selected_model']}: {str(e)}")
                # Some models might not be available or configured, that's OK for this test
                error_str = str(e).lower()
                if any(x in error_str for x in ["api key", "not found", "model_not_found", "verified", "404"]):
                    print(f"Skipping {result['selected_model']} - not configured or not available")
                else:
                    raise
        
        # Test parallelbest mode
        print("\n\n=== Testing parallelbest mode ===")
        messages = [{"role": "user", "content": "Make factorial.py with a factorial function"}]
        try:
            response, metadata = router.parallelbest_route(messages, max_tokens=100)
            print(f"\nParallelbest mode result:")
            print(f"Selected best model: {metadata['selected_model']}")
            print(f"Best model reasoning: {metadata['evaluation']['reasoning']}")
            print(f"Model ranking: {metadata['evaluation']['ranking']}")
            print(f"Response preview: {response.choices[0].message.content[:150]}...")
            
            # Verify the response
            assert response.choices[0].message.content
            assert metadata['parallelbest_mode'] is True
            assert 'all_responses' in metadata
            assert len(metadata['all_responses']) > 0
        except Exception as e:
            print(f"Error in parallelbest mode: {str(e)}")
            # Check if it's due to missing models
            if "verified" in str(e).lower() or "404" in str(e).lower():
                print("Some models not available, continuing...")
            else:
                raise
        
        # Test parallelsynthetize mode
        print("\n\n=== Testing parallelsynthetize mode ===")
        messages = [{"role": "user", "content": "Make subtraction.py with a subtraction function"}]
        try:
            response, metadata = router.parallelsynthetize_route(messages, max_tokens=100)
            print(f"\nParallelsynthetize mode result:")
            print(f"Models used: {metadata['models_used']}")
            print(f"Synthesized response preview: {response.choices[0].message.content[:150]}...")
            
            # Verify the response
            assert response.choices[0].message.content
            assert metadata['synthesis_mode'] is True
            assert metadata['parallelsynthetize_mode'] is True
            assert 'all_responses' in metadata
            assert len(metadata['all_responses']) > 0
        except Exception as e:
            print(f"Error in parallelsynthetize mode: {str(e)}")
            # Check if it's due to missing models
            if "verified" in str(e).lower() or "404" in str(e).lower():
                print("Some models not available, continuing...")
            else:
                raise

