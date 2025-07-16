#!/usr/bin/env python3
"""Debug script to test parallelsynthetize_route with logging"""

import os
import sys
import time
import logging
from router import AIRouter
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_individual_models():
    """Test each model individually to identify which one is hanging"""
    config = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": "https://api.openai.com/v1"
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        },
        "claude_code": {
            "api_key": "dummy"  # Claude Code runs locally
        },
        "xai": {
            "api_key": os.getenv("XAI_API_KEY", ""),
            "base_url": "https://api.x.ai/v1"
        },
        "google": {
            "api_key": os.getenv("GOOGLE_API_KEY", "")
        }
    }
    
    router = AIRouter(config)
    
    # Simple test message
    messages = [{"role": "user", "content": "What is 2+2?"}]
    
    # Test each model individually
    models_to_test = [
        ("gpt-4o", "openai:gpt-4o"),
        ("claude-opus", "anthropic:claude-opus-4-20250514"),
        ("o3", "openai:o3-mini"),
        ("gpt-4o-mini", "openai:gpt-4o-mini"),
        ("claude-code", "claude_code:Claude"),
        ("grok-4", "xai:grok-4"),
        ("gemini-2.5-pro", "google:gemini-2.5-pro")
    ]
    
    for model_name, model_id in models_to_test:
        logger.info(f"\nTesting {model_name} ({model_id})...")
        start_time = time.time()
        
        try:
            response = router.client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=100
            )
            elapsed_time = time.time() - start_time
            logger.info(f"✓ {model_name} responded in {elapsed_time:.2f}s")
            logger.debug(f"Response: {response.choices[0].message.content[:100]}...")
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"✗ {model_name} failed after {elapsed_time:.2f}s: {str(e)}")

def test_parallel_route():
    """Test the full parallelsynthetize_route"""
    config = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": "https://api.openai.com/v1"
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        },
        "claude_code": {
            "api_key": "dummy"  # Claude Code runs locally
        },
        "xai": {
            "api_key": os.getenv("XAI_API_KEY", ""),
            "base_url": "https://api.x.ai/v1"
        },
        "google": {
            "api_key": os.getenv("GOOGLE_API_KEY", "")
        }
    }
    
    router = AIRouter(config)
    
    # Simple test message
    messages = [{"role": "user", "content": "What is 2+2?"}]
    
    logger.info("\nTesting parallelsynthetize_route...")
    start_time = time.time()
    
    try:
        response, metadata = router.parallelsynthetize_route(
            messages, 
            max_tokens=100,
            temperature=0.2
        )
        elapsed_time = time.time() - start_time
        logger.info(f"✓ parallelsynthetize_route completed in {elapsed_time:.2f}s")
        logger.info(f"Best model: {metadata.get('best_model', 'Unknown')}")
        logger.debug(f"Response: {response.choices[0].message.content[:100]}...")
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"✗ parallelsynthetize_route failed after {elapsed_time:.2f}s: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--individual":
        test_individual_models()
    else:
        logger.info("Testing individual models first to identify issues...")
        test_individual_models()
        logger.info("\n" + "="*60 + "\n")
        test_parallel_route()