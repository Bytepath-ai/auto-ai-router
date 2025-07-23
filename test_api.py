#!/usr/bin/env python3
"""
Test script for AI Router API
Tests all available endpoints with various scenarios
"""

import requests
import json
import time
from typing import Dict, Any

# API configuration
API_URL = "http://localhost:5000"

headers = {
    "Content-Type": "application/json"
}

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")

def print_response(response: requests.Response, endpoint: str):
    """Print formatted response"""
    print(f"Endpoint: {endpoint}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 40)

def test_health_check():
    """Test the health check endpoint"""
    print_section("Testing Health Check Endpoint")
    
    response = requests.get(f"{API_URL}/health")
    print_response(response, "GET /health")

def test_list_models():
    """Test the models listing endpoint"""
    print_section("Testing Models Listing Endpoint")
    
    response = requests.get(f"{API_URL}/models")
    print_response(response, "GET /models")

def test_route():
    """Test the basic routing endpoint"""
    print_section("Testing Route Endpoint")
    
    # Test 1: Simple routing example
    data = {
        "messages": [
            {"role": "user", "content": "Write a haiku about programming"}
        ],
        "temperature": 0.8
    }
    
    response = requests.post(f"{API_URL}/route", 
                            headers=headers, 
                            data=json.dumps(data))
    print("Test 1: Simple routing")
    print_response(response, "POST /route")
    
    # Test 2: With max_tokens parameter
    data_with_tokens = {
        "messages": [
            {"role": "user", "content": "Explain recursion in one sentence"}
        ],
        "temperature": 0.5,
        "max_tokens": 50
    }
    
    response = requests.post(f"{API_URL}/route", 
                            headers=headers, 
                            data=json.dumps(data_with_tokens))
    print("\nTest 2: With max_tokens parameter")
    print_response(response, "POST /route")

def test_route_with_metadata():
    """Test the routing with metadata endpoint"""
    print_section("Testing Route with Metadata Endpoint")
    
    data = {
        "messages": [
            {"role": "user", "content": "What's the capital of France?"}
        ],
        "temperature": 0.3
    }
    
    response = requests.post(f"{API_URL}/route_with_metadata", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /route_with_metadata")

def test_parallelbest():
    """Test the parallel best route endpoint"""
    print_section("Testing Parallel Best Route Endpoint")
    
    data = {
        "messages": [
            {"role": "user", "content": "Generate a creative story title"}
        ],
        "temperature": 0.9
    }
    
    response = requests.post(f"{API_URL}/parallelbest", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /parallelbest")

def test_parallelsynthetize():
    """Test the parallel synthetize route endpoint"""
    print_section("Testing Parallel Synthetize Route Endpoint")
    
    data = {
        "messages": [
            {"role": "user", "content": "What are the benefits of exercise?"}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(f"{API_URL}/parallelsynthetize", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /parallelsynthetize")

def test_analyze():
    """Test the analyze prompt endpoint"""
    print_section("Testing Analyze Prompt Endpoint")
    
    data = {
        "prompt": "Write a Python function to calculate the factorial of a number"
    }
    
    response = requests.post(f"{API_URL}/analyze", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /analyze")

def test_error_handling():
    """Test error handling with invalid requests"""
    print_section("Testing Error Handling")
    
    # Test 1: Missing messages field
    print("Test 1: Missing messages field")
    data = {"temperature": 0.7}
    response = requests.post(f"{API_URL}/route", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /route (invalid)")
    
    # Test 2: Empty messages list
    print("\nTest 2: Empty messages list")
    data = {"messages": []}
    response = requests.post(f"{API_URL}/route", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /route (invalid)")
    
    # Test 3: Invalid message format
    print("\nTest 3: Invalid message format")
    data = {"messages": ["invalid message format"]}
    response = requests.post(f"{API_URL}/route", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /route (invalid)")
    
    # Test 4: Missing prompt field in analyze
    print("\nTest 4: Missing prompt field in analyze")
    data = {"invalid_field": "test"}
    response = requests.post(f"{API_URL}/analyze", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /analyze (invalid)")
    
    # Test 5: 404 Not Found
    print("\nTest 5: 404 Not Found")
    response = requests.get(f"{API_URL}/nonexistent")
    print_response(response, "GET /nonexistent")

def test_conversation():
    """Test a multi-turn conversation"""
    print_section("Testing Multi-turn Conversation")
    
    messages = [
        {"role": "user", "content": "Hi, I'm learning Python"},
        {"role": "assistant", "content": "That's great! Python is an excellent language to learn."},
        {"role": "user", "content": "What should I learn first?"}
    ]
    
    data = {
        "messages": messages,
        "temperature": 0.7
    }
    
    response = requests.post(f"{API_URL}/route", 
                            headers=headers, 
                            data=json.dumps(data))
    print_response(response, "POST /route (conversation)")

def main():
    """Run all tests"""
    print("AI Router API Test Suite")
    print(f"Testing API at: {API_URL}")
    print("Note: Make sure the API server is running with 'python api.py'")
        
    # Run all tests
    try:
        test_health_check()
        time.sleep(1)  # Small delay between tests
        
        test_list_models()
        time.sleep(1)
        
        test_route()
        time.sleep(1)
        
        test_route_with_metadata()
        time.sleep(1)
        
        test_parallelbest()
        time.sleep(1)
        
        test_parallelsynthetize()
        time.sleep(1)
        
        test_analyze()
        time.sleep(1)
        
        test_error_handling()
        time.sleep(1)
        
        test_conversation()
        
        print_section("All Tests Completed")
        print("✓ Test suite finished successfully")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the API server is running with: python api.py")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    main()