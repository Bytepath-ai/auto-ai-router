#!/usr/bin/env python3
"""
Test script for Tavily integration with AI Router

This script demonstrates how the AI Router automatically includes Tavily tool
for all LLM calls. Each test makes only a single LLM call.
"""

import json
from router import AIRouter

# Configuration for AI providers (using environment variables)
config = {}

# Initialize router
router = AIRouter(config)

def check_tool_calls(response):
    """Check if the model made any tool calls"""
    message = response.choices[0].message
    
    if hasattr(message, 'tool_calls') and message.tool_calls:
        print("\n📋 Model requested tool calls:")
        for tool_call in message.tool_calls:
            print(f"  - Function: {tool_call.function.name}")
            args = json.loads(tool_call.function.arguments)
            print(f"    Arguments: {args}")
        return True
    return False

print("Testing Tavily integration with AI Router...")
print("=" * 50)

# Test 1: Basic routing - checking if Tavily tool is available
print("\nTest 1: Basic routing (checking tool availability)")
messages = [
    {"role": "user", "content": "What tools do you have available? Can you search the web?"}
]
print("User prompt:", messages[0]["content"])

try:
    response = router.route(messages)
    print("\nModel's response:", response.choices[0].message.content)
    check_tool_calls(response)
except Exception as e:
    print(f"Error: {e}")

# Test 2: Query that might trigger tool usage
print("\n" + "=" * 50)
print("\nTest 2: Real-time information query")

weather_messages = [
    {"role": "user", "content": "What is the current weather in Tokyo, Japan?"}
]
print("User prompt:", weather_messages[0]["content"])

try:
    response = router.route(weather_messages)
    print("\nModel's response:", response.choices[0].message.content[:400] + "..." if len(response.choices[0].message.content) > 400 else response.choices[0].message.content)
    if check_tool_calls(response):
        print("\nNote: Model requested web search. In a full implementation, you would execute the search and make another call.")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Routing with metadata
print("\n" + "=" * 50)
print("\nTest 3: Search query with routing metadata")

search_messages = [
    {"role": "user", "content": "Search for the latest developments in quantum computing in 2024"}
]
print("User prompt:", search_messages[0]["content"])

try:
    response, metadata = router.route_with_metadata(search_messages)
    print(f"\nRouting metadata:")
    print(f"  Selected model: {metadata['selected_model']}")
    print(f"  Model ID: {metadata['model_id']}")
    print(f"  Reasoning: {metadata['reasoning']}")
    print(f"  Confidence: {metadata['confidence']:.2%}")
    
    print("\nModel's response:", response.choices[0].message.content[:400] + "..." if len(response.choices[0].message.content) > 400 else response.choices[0].message.content)
    check_tool_calls(response)
except Exception as e:
    print(f"Error: {e}")

# Test 4: Complex analysis query
print("\n" + "=" * 50)
print("\nTest 4: Complex query requiring current data")

analysis_messages = [
    {"role": "user", "content": "What are the current stock prices of the top 5 tech companies?"}
]
print("User prompt:", analysis_messages[0]["content"])

try:
    response = router.route(analysis_messages)
    print("\nModel's response:", response.choices[0].message.content[:500] + "..." if len(response.choices[0].message.content) > 500 else response.choices[0].message.content)
    check_tool_calls(response)
except Exception as e:
    print(f"Error: {e}")

# Test 5: Parallel best mode
print("\n" + "=" * 50)
print("\nTest 5: Parallel best mode (single call)")

parallel_messages = [
    {"role": "user", "content": "What are the latest AI breakthroughs announced this week?"}
]
print("User prompt:", parallel_messages[0]["content"])

try:
    response, metadata = router.parallelbest_route(parallel_messages)
    
    print(f"\nParallel routing results:")
    print(f"  Best model: {metadata['evaluation']['best_model']}")
    print(f"  Model ranking: {metadata['evaluation']['ranking']}")
    print(f"  Task category: {metadata['task_info']['task_category']}")
    print(f"  Task name: {metadata['task_info']['task_name']}")
    
    print(f"\nBest response: {response.choices[0].message.content[:500]}...")
except Exception as e:
    print(f"Error: {e}")

# Test 6: Parallel synthesis mode
print("\n" + "=" * 50)
print("\nTest 6: Parallel synthesis mode (single call)")

synthesis_messages = [
    {"role": "user", "content": "What's the current status of self-driving car technology?"}
]
print("User prompt:", synthesis_messages[0]["content"])

try:
    response, metadata = router.parallelsynthetize_route(synthesis_messages)
    
    print(f"\nSynthesis results:")
    print(f"  Models used: {metadata['models_used']}")
    print(f"  Best individual model: {metadata['best_individual_model']}")
    
    print(f"\nSynthesized response: {response.choices[0].message.content[:500]}...")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Testing complete!")
print("\nKey observations:")
print("- The Tavily tool is automatically included in all routing methods")
print("- Models may choose to use the tool when they need current information")
print("- Each test made only a single LLM call")
print("- Tool calls (if any) are indicated but not executed in this demo")

# Note: To use this script, make sure you have:
# 1. Set TAVILY_API_KEY environment variable or in .env file
# 2. Set API keys for AI providers (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
# 3. Installed required packages: pip install tavily-python aisuite python-dotenv