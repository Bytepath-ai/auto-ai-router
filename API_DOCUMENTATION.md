# AI Router Flask API Documentation

## Overview

The AI Router API provides HTTP endpoints for intelligent AI model routing. It automatically selects the best AI model based on your prompt characteristics or can call multiple models in parallel.

## Base URL

```
http://localhost:5000
```

## Authentication

No authentication is required for API endpoints.

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Router API",
  "version": "1.0.0"
}
```

### 2. List Models

Get information about all available models.

**Endpoint:** `GET /models`

**Response:**
```json
{
  "models": {
    "gpt-4o": {
      "name": "GPT-4o",
      "provider": "openai",
      "model_id": "gpt-4o",
      "strengths": ["general knowledge", "reasoning", ...],
      "cost_per_1k_tokens": 0.00375
    },
    "claude-opus": {
      "name": "Claude Opus 4",
      "provider": "anthropic",
      "model_id": "claude-opus-4-20250514",
      "strengths": ["code generation", "programming solutions", ...],
      "cost_per_1k_tokens": 0.015
    },
    ...
  },
  "router_model": "google:gemini-2.5-pro"
}
```

### 3. Route Request

Route a request to the most appropriate AI model based on the prompt.

**Endpoint:** `POST /route`

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Write a Python function to calculate factorial"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Response:**
```json
{
  "response": "Here's a Python function to calculate factorial:\n\n```python\ndef factorial(n):\n    if n < 0:\n        raise ValueError(\"Factorial is not defined for negative numbers\")\n    elif n == 0 or n == 1:\n        return 1\n    else:\n        return n * factorial(n - 1)\n```",
  "model": "anthropic:claude-opus-4-20250514"
}
```

### 4. Route with Metadata

Route a request and get detailed metadata about the routing decision.

**Endpoint:** `POST /route_with_metadata`

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Explain quantum computing in simple terms"}
  ],
  "temperature": 0.5
}
```

**Response:**
```json
{
  "response": "Quantum computing is like having a magical computer that can explore many possibilities at once...",
  "metadata": {
    "selected_model": "gpt-4o",
    "model_id": "openai:gpt-4o",
    "reasoning": "This is a general knowledge question requiring clear explanation, which is a strength of GPT-4o",
    "confidence": 0.85,
    "estimated_cost_per_1k": 0.00375
  }
}
```

### 5. Parallel Best Route

Call all models in parallel and return the best response.

**Endpoint:** `POST /parallelbest`

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "What's the most efficient sorting algorithm for large datasets?"}
  ]
}
```

**Response:**
```json
{
  "response": "For large datasets, the most efficient sorting algorithm depends on several factors...",
  "metadata": {
    "selected_model": "claude-opus",
    "model_id": "anthropic:claude-opus-4-20250514",
    "evaluation": {
      "best_model": "Claude Opus 4",
      "reasoning": "Claude Opus provided the most comprehensive and technically accurate response",
      "ranking": ["Claude Opus 4", "O3", "GPT-4o", ...]
    },
    "task_info": {
      "task_name": "Sorting algorithm efficiency analysis",
      "task_category": "technical"
    },
    "scoring": {
      "scores": {
        "Claude Opus 4": 9,
        "O3": 8,
        "GPT-4o": 7,
        ...
      },
      "brief_reasoning": "Claude Opus demonstrated superior technical depth"
    },
    "parallelbest_mode": true
  },
  "all_responses": [
    {
      "model": "Claude Opus 4",
      "response": "For large datasets, the most efficient sorting algorithm depends on..."
    },
    {
      "model": "GPT-4o",
      "response": "When dealing with large datasets, several sorting algorithms..."
    },
    ...
  ]
}
```

### 6. Parallel Synthesize Route

Call multiple models in parallel and synthesize their responses into one comprehensive answer.

**Endpoint:** `POST /parallelsynthetize`

**Request Body:**
```json
{
  "messages": [
    {"role": "user", "content": "Compare REST APIs vs GraphQL for modern web development"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Response:**
```json
{
  "synthesized_response": "When comparing REST APIs and GraphQL for modern web development, several key differences emerge:\n\n[Comprehensive synthesis combining insights from multiple models...]",
  "metadata": {
    "synthesis_mode": true,
    "parallelsynthetize_mode": true,
    "models_used": ["Claude Code", "Claude Opus 4", "O3", "Grok-4", "Gemini 2.5 Pro"],
    "task_info": {
      "task_name": "REST vs GraphQL comparison",
      "task_category": "technical"
    },
    "best_individual_model": "Claude Opus 4"
  },
  "models_used": ["Claude Code", "Claude Opus 4", "O3", "Grok-4", "Gemini 2.5 Pro"]
}
```

### 7. Analyze Prompt

Analyze a prompt without sending it to any model.

**Endpoint:** `POST /analyze`

**Request Body:**
```json
{
  "prompt": "Debug this React component that's causing infinite re-renders"
}
```

**Response:**
```json
{
  "selected_model": "claude-code",
  "model_id": "claude_code:claude",
  "reasoning": "This is an in-repo debugging task for React, which is Claude Code's strength",
  "confidence": 0.92,
  "estimated_cost_per_1k": 0.0
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Missing or invalid API key
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error

## Example Usage

### Python Example

```python
import requests
import json

# API configuration
API_URL = "http://localhost:5000"

headers = {
    "Content-Type": "application/json"
}

# Simple routing example
data = {
    "messages": [
        {"role": "user", "content": "Write a haiku about programming"}
    ],
    "temperature": 0.8
}

response = requests.post(f"{API_URL}/route", 
                        headers=headers, 
                        data=json.dumps(data))

result = response.json()
print(f"Response from {result.get('model', 'unknown')}:")
print(result['response'])
```

### cURL Example

```bash
# Simple route request
curl -X POST http://localhost:5000/route \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is machine learning?"}
    ]
  }'

# Parallel synthesis request
curl -X POST http://localhost:5000/parallelsynthetize \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain the future of AI"}
    ],
    "max_tokens": 1500
  }'
```

### JavaScript/Node.js Example

```javascript
const API_URL = 'http://localhost:5000';

async function routeRequest(prompt) {
  const response = await fetch(`${API_URL}/route`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messages: [
        { role: 'user', content: prompt }
      ],
      temperature: 0.7
    })
  });

  const result = await response.json();
  console.log(`Model used: ${result.model}`);
  console.log(`Response: ${result.response}`);
}

// Usage
routeRequest('How do I center a div in CSS?');
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# API Keys for different providers
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
XAI_API_KEY=your-xai-key

# Server configuration
PORT=5000
DEBUG=False
```

### Running the API

1. Install dependencies:
```bash
pip install flask flask-cors python-dotenv aisuite
```

2. Start the server:
```bash
python api.py
```

The API will be available at `http://localhost:5000`.

## Rate Limiting

The API does not implement rate limiting by default. You should add rate limiting in production using tools like:
- Flask-Limiter
- nginx rate limiting
- API gateway solutions

## Notes

- All model parameters (temperature, max_tokens, etc.) are passed through to the underlying models
- The `parallelbest` and `parallelsynthetize` endpoints may take longer due to calling multiple models
- Model availability depends on having the corresponding API keys configured
- Response times vary based on the selected model and prompt complexity