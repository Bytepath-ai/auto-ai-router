#!/usr/bin/env python3
"""
Test script for evaluating parallelsynthetize_route function
"""

import os
import json
from router import AIRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_parallelsynthetize_route():
    """Test the parallelsynthetize_route function with various prompts"""
    
    # Initialize router
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
    
    # Test prompts
    test_prompts = [
        {
            "category": "coding",
            "prompt": "Write a Python function to calculate the factorial of a number recursively."
        },
        {
            "category": "reasoning",
            "prompt": "Explain why the sky appears blue during the day but red/orange during sunrise and sunset."
        },
        {
            "category": "general",
            "prompt": "What are the main differences between supervised and unsupervised learning?"
        }
    ]
    
    results = []
    
    for test_case in test_prompts:
        print(f"\n\nTesting category: {test_case['category']}")
        print(f"Prompt: {test_case['prompt']}")
        print("-" * 80)
        
        messages = [{"role": "user", "content": test_case['prompt']}]
        
        try:
            # Call parallelsynthetize_route
            response, metadata = router.parallelsynthetize_route(messages, max_tokens=500)
            
            # Extract synthesized response
            synthesized_content = response.choices[0].message.content
            
            result = {
                "category": test_case['category'],
                "prompt": test_case['prompt'],
                "synthesized_response": synthesized_content,
                "metadata": metadata,
                "models_used": metadata.get("models_used", []),
                "best_individual_model": metadata.get("best_individual_model", "Unknown"),
                "task_info": metadata.get("task_info", {}),
                "scoring": metadata.get("scoring", {})
            }
            
            results.append(result)
            
            print(f"\nSynthesized Response:")
            print(synthesized_content)
            print(f"\nModels Used: {', '.join(metadata.get('models_used', []))}")
            print(f"Best Individual Model: {metadata.get('best_individual_model', 'Unknown')}")
            
            # Show individual scores
            if 'scoring' in metadata and 'scores' in metadata['scoring']:
                print("\nIndividual Model Scores:")
                for model, score in metadata['scoring']['scores'].items():
                    print(f"  - {model}: {score}/10")
            
        except Exception as e:
            print(f"Error testing prompt: {str(e)}")
            results.append({
                "category": test_case['category'],
                "prompt": test_case['prompt'],
                "error": str(e)
            })
    
    # Save results
    with open("parallelsynthetize_route_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n\nTest results saved to parallelsynthetize_route_results.json")
    
    # Generate summary report
    print("\n\nSUMMARY REPORT")
    print("=" * 80)
    print(f"Total tests run: {len(test_prompts)}")
    print(f"Successful: {sum(1 for r in results if 'error' not in r)}")
    print(f"Failed: {sum(1 for r in results if 'error' in r)}")
    
    # Show task categorization
    print("\nTask Categorization:")
    for result in results:
        if 'task_info' in result:
            task_info = result['task_info']
            print(f"  - {task_info.get('task_name', 'Unknown')}: {task_info.get('task_category', 'Unknown')}")

if __name__ == "__main__":
    test_parallelsynthetize_route()