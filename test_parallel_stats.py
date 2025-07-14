#!/usr/bin/env python3
"""Test script for parallel route statistics tracking"""

from router import AIRouter
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize router
router = AIRouter()

# Test queries of different types
test_queries = [
    # {
    #     "prompt": "Write a Python function that implements binary search on a sorted list",
    #     "expected_category": "coding"
    # },
    {
        "prompt": "Explain the implications of quantum computing on modern cryptography",
        "expected_category": "reasoning"
    },
    {
        "prompt": "What's the weather like today?",
        "expected_category": "simple"
    },
#     {
#         "prompt": "Create a haiku about artificial intelligence",
#         "expected_category": "creative"
#     },
#     {
#         "prompt": "Analyze the time complexity of merge sort algorithm",
#         "expected_category": "analysis"
#     }
]

print("Testing parallel route statistics tracking...")
print("=" * 60)

for i, query in enumerate(test_queries, 1):
    print(f"\nTest {i}: {query['expected_category'].upper()} task")
    print(f"Prompt: {query['prompt'][:50]}...")
    
    try:
        # Create messages format expected by the router
        messages = [
            {"role": "user", "content": query['prompt']}
        ]
        
        # Call parallelbest_route which now tracks statistics
        response, metadata = router.parallelbest_route(messages)
        
        # Display results
        print(f"Task Name: {metadata['task_info']['task_name']}")
        print(f"Task Category: {metadata['task_info']['task_category']}")
        print(f"Best Model: {metadata['evaluation']['best_model']}")
        print(f"Scores: {metadata['scoring']['scores']}")
        print("-" * 60)
        
        # Small delay between requests
        time.sleep(1)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        continue

print(f"\nStatistics have been saved to: {router.stats_file}")
print("\nYou can view the statistics by opening the CSV file.")