# AI Router

An intelligent AI model router that automatically selects the best AI model for your prompt or can run multiple models in parallel for optimal results.

## Flask API

### Running the API

1. Install dependencies:
```bash
pip install flask flask-cors python-dotenv aisuite
```

2. Copy the `.env.sample` file to `.env` and fill in your API keys:
```bash
cp .env.sample .env
```

3. Edit the `.env` file with your API keys. The available keys are:
   - `OPENAI_API_KEY` - Required for GPT-4o and GPT-4o-mini models
   - `ANTHROPIC_API_KEY` - Required for Claude models
   - `XAI_API_KEY` - Required for X.AI models (if using O3)
   - `GOOGLE_API_KEY` - Required for Google models
   - `GOOGLE_PROJECT_ID` - Required for Google models
   - `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google service account JSON
   - `GOOGLE_REGION` - Google Cloud region

4. Follow the provider-specific setup guides in the `guides/` directory:
   - [Anthropic Setup Guide](guides/anthropic.md) - For Claude models
   - [Google Setup Guide](guides/google.md) - For Google models
   - [OpenAI Setup Guide](guides/openai.md) - For GPT models
   - [X.AI Setup Guide](guides/xai.md) - For X.AI models

   Each guide contains detailed instructions on how to obtain API keys and configure your environment for that specific provider.

5. Start the server:
```bash
python api.py
```

The API will be available at `http://localhost:5000`.

### API Documentation

#### Overview

The AI Router API provides HTTP endpoints for intelligent AI model routing. It automatically selects the best AI model based on your prompt characteristics or can call multiple models in parallel.

#### Base URL

```
http://localhost:5000
```

#### Authentication

No authentication is required for API endpoints.

#### Endpoints

##### 1. Health Check

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

##### 2. List Models

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

##### 3. Route Request

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

##### 4. Route with Metadata

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

##### 5. Parallel Best Route

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

##### 6. Parallel Synthesize Route

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

##### 7. Analyze Prompt

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

#### Error Responses

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

#### Example Usage

##### Python Example

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

##### cURL Example

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

##### JavaScript/Node.js Example

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

#### Configuration

##### Environment Variables

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

#### Rate Limiting

The API does not implement rate limiting by default. You should add rate limiting in production using tools like:
- Flask-Limiter
- nginx rate limiting
- API gateway solutions

#### Notes

- All model parameters (temperature, max_tokens, etc.) are passed through to the underlying models
- The `parallelbest` and `parallelsynthetize` endpoints may take longer due to calling multiple models
- Model availability depends on having the corresponding API keys configured
- Response times vary based on the selected model and prompt complexity

## Setup

1. Install the required dependencies:
```bash
pip install aisuite python-dotenv
```

2. Copy the `.env.sample` file to `.env` and fill in your API keys:
```bash
cp .env.sample .env
```

3. Edit the `.env` file with your API keys. The available keys are:
   - `OPENAI_API_KEY` - Required for GPT-4o and GPT-4o-mini models
   - `ANTHROPIC_API_KEY` - Required for Claude models
   - `XAI_API_KEY` - Required for X.AI models (if using O3)
   - `GOOGLE_API_KEY` - Required for Google models
   - `GOOGLE_PROJECT_ID` - Required for Google models
   - `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google service account JSON
   - `GOOGLE_REGION` - Google Cloud region

4. Follow the provider-specific setup guides in the `guides/` directory:
   - [Anthropic Setup Guide](guides/anthropic.md) - For Claude models
   - [Google Setup Guide](guides/google.md) - For Google models
   - [OpenAI Setup Guide](guides/openai.md) - For GPT models
   - [X.AI Setup Guide](guides/xai.md) - For X.AI models

   Each guide contains detailed instructions on how to obtain API keys and configure your environment for that specific provider.

## Usage

### Basic Routing

The simplest way to use the AI Router is to let it automatically select the best model:

```python
from router import AIRouter

# Initialize the router
router = AIRouter()

# Create your messages
messages = [{"role": "user", "content": "Write a Python function to calculate fibonacci"}]

# Route to the best model automatically
response = router.route(messages)
print(response.choices[0].message.content)
```

### Analyzing Prompts

You can analyze a prompt to see which model would be selected and why:

```python
# Analyze which model would be best for a prompt
analysis = router.analyze_prompt("Prove that sqrt(2) is irrational")
print(f"Selected model: {analysis['selected_model']}")
print(f"Confidence: {analysis['confidence']:.2%}")
print(f"Reasoning: {analysis['reasoning']}")
```

### Getting Routing Metadata

To get both the response and detailed routing information:

```python
response, metadata = router.route_with_metadata(messages)

print(f"Model used: {metadata['selected_model']}")
print(f"Model ID: {metadata['model_id']}")
print(f"Confidence: {metadata['confidence']}")
print(f"Reasoning: {metadata['reasoning']}")
print(f"Response: {response.choices[0].message.content}")
```

### Parallel Routing Modes

#### Parallel Best Mode

This mode calls all models in parallel and selects the best response:

```python
response, metadata = router.parallelbest_route(messages)

# The response contains the best answer
print(response.choices[0].message.content)

# Metadata includes evaluation details
print(f"Best model: {metadata['evaluation']['best_model']}")
print(f"Ranking: {metadata['evaluation']['ranking']}")
print(f"All responses: {len(metadata['all_responses'])}")
```

**Statistics Tracking**: The `parallelbest_route` method now automatically tracks:
- Task category (coding, reasoning, general, creative, analysis, simple)
- Best model selection
- All statistics are saved to `parallel_route_stats.txt` (simple format: task_category,best_model)

To view statistics:
```bash
python view_stats.py
```

#### Parallel Synthesize Mode

This mode combines insights from all models into a comprehensive response:

```python
response, metadata = router.parallelsynthetize_route(messages)

# The response is a synthesis of all model outputs
print(response.choices[0].message.content)

# Metadata shows which models contributed
print(f"Models used: {metadata['models_used']}")
print(f"Number of responses: {len(metadata['all_responses'])}")
```

## Advanced Configuration

You can provide custom configuration when initializing the router:

```python
config = {
    "openai": {"api_key": "your-key"},
    "anthropic": {"api_key": "your-key"}
}

router = AIRouter(config=config)
```

## Cost Considerations

Each model has different cost implications:
- **Claude Code**: Free when running locally
- **GPT-4o-mini**: Most cost-efficient (~$0.00015 per 1k tokens)
- **GPT-4o**: Moderate cost (~$0.00375 per 1k tokens)
- **Claude Opus 4**: Higher cost (~$0.015 per 1k tokens)
- **O3**: Premium pricing (~$0.020 per 1k tokens)

## Examples

Run the comprehensive examples to see all features in action:

```bash
python router_examples.py
```

This will demonstrate:
- Basic routing with various prompt types
- Parallel best mode for quality comparison
- Parallel synthesize mode for comprehensive answers
- Routing with metadata for transparency

## When to Use Each Mode

- **Standard Routing (`route`)**: Best for most use cases where you want fast, efficient responses
- **Parallel Best (`parallelbest_route`)**: When quality is paramount and you want the absolute best response
- **Parallel Synthesize (`parallelsynthetize_route`)**: When you need comprehensive coverage combining multiple perspectives

# aisuite

[![PyPI](https://img.shields.io/pypi/v/aisuite)](https://pypi.org/project/aisuite/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Simple, unified interface to multiple Generative AI providers.

`aisuite` makes it easy for developers to use multiple LLM through a standardized interface. Using an interface similar to OpenAI's, `aisuite` makes it easy to interact with the most popular LLMs and compare the results. It is a thin wrapper around python client libraries, and allows creators to seamlessly swap out and test responses from different LLM providers without changing their code. Today, the library is primarily focussed on chat completions. We will expand it cover more use cases in near future.

Currently supported providers are:
- Anthropic
- AWS
- Azure
- Cerebras
- Google
- Groq
- HuggingFace Ollama
- Mistral
- OpenAI
- Sambanova
- Watsonx

To maximize stability, `aisuite` uses either the HTTP endpoint or the SDK for making calls to the provider.

## Installation

You can install just the base `aisuite` package, or install a provider's package along with `aisuite`.

This installs just the base package without installing any provider's SDK.

```shell
pip install aisuite
```

This installs aisuite along with anthropic's library.

```shell
pip install 'aisuite[anthropic]'
```

This installs all the provider-specific libraries

```shell
pip install 'aisuite[all]'
```

## Set up

To get started, you will need API Keys for the providers you intend to use. You'll need to
install the provider-specific library either separately or when installing aisuite.

The API Keys can be set as environment variables, or can be passed as config to the aisuite Client constructor.
You can use tools like [`python-dotenv`](https://pypi.org/project/python-dotenv/) or [`direnv`](https://direnv.net/) to set the environment variables manually. Please take a look at the `examples` folder to see usage.

Here is a short example of using `aisuite` to generate chat completion responses from gpt-4o and claude-3-5-sonnet.

Set the API keys.

```shell
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Use the python client.

```python
import aisuite as ai
client = ai.Client()

models = ["openai:gpt-4o", "anthropic:claude-3-5-sonnet-20240620"]

messages = [
    {"role": "system", "content": "Respond in Pirate English."},
    {"role": "user", "content": "Tell me a joke."},
]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.75
    )
    print(response.choices[0].message.content)

```

Note that the model name in the create() call uses the format - `<provider>:<model-name>`.
`aisuite` will call the appropriate provider with the right parameters based on the provider value.
For a list of provider values, you can look at the directory - `aisuite/providers/`. The list of supported providers are of the format - `<provider>_provider.py` in that directory. We welcome  providers adding support to this library by adding an implementation file in this directory. Please see section below for how to contribute.

For more examples, check out the `examples` directory where you will find several notebooks that you can run to experiment with the interface.

## Adding support for a provider

We have made easy for a provider or volunteer to add support for a new platform.

### Naming Convention for Provider Modules

We follow a convention-based approach for loading providers, which relies on strict naming conventions for both the module name and the class name. The format is based on the model identifier in the form `provider:model`.

- The provider's module file must be named in the format `<provider>_provider.py`.
- The class inside this module must follow the format: the provider name with the first letter capitalized, followed by the suffix `Provider`.

#### Examples

- **Hugging Face**:
  The provider class should be defined as:

  ```python
  class HuggingfaceProvider(BaseProvider)
  ```

  in providers/huggingface_provider.py.
  
- **OpenAI**:
  The provider class should be defined as:

  ```python
  class OpenaiProvider(BaseProvider)
  ```

  in providers/openai_provider.py

This convention simplifies the addition of new providers and ensures consistency across provider implementations.

## Tool Calling

`aisuite` provides a simple abstraction for tool/function calling that works across supported providers. This is in addition to the regular abstraction of passing JSON spec of the tool to the `tools` parameter. The tool calling abstraction makes it easy to use tools with different LLMs without changing your code.

There are two ways to use tools with `aisuite`:

### 1. Manual Tool Handling

This is the default behavior when `max_turns` is not specified.
You can pass tools in the OpenAI tool format:

```python
def will_it_rain(location: str, time_of_day: str):
    """Check if it will rain in a location at a given time today.
    
    Args:
        location (str): Name of the city
        time_of_day (str): Time of the day in HH:MM format.
    """
    return "YES"

tools = [{
    "type": "function",
    "function": {
        "name": "will_it_rain",
        "description": "Check if it will rain in a location at a given time today",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Name of the city"
                },
                "time_of_day": {
                    "type": "string",
                    "description": "Time of the day in HH:MM format."
                }
            },
            "required": ["location", "time_of_day"]
        }
    }
}]

response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=messages,
    tools=tools
)
```

### 2. Automatic Tool Execution

When `max_turns` is specified, you can pass a list of callable Python functions as the `tools` parameter. `aisuite` will automatically handle the tool calling flow:

```python
def will_it_rain(location: str, time_of_day: str):
    """Check if it will rain in a location at a given time today.
    
    Args:
        location (str): Name of the city
        time_of_day (str): Time of the day in HH:MM format.
    """
    return "YES"

client = ai.Client()
messages = [{
    "role": "user",
    "content": "I live in San Francisco. Can you check for weather "
               "and plan an outdoor picnic for me at 2pm?"
}]

# Automatic tool execution with max_turns
response = client.chat.completions.create(
    model="openai:gpt-4o",
    messages=messages,
    tools=[will_it_rain],
    max_turns=2  # Maximum number of back-and-forth tool calls
)
print(response.choices[0].message.content)
```

When `max_turns` is specified, `aisuite` will:
1. Send your message to the LLM
2. Execute any tool calls the LLM requests
3. Send the tool results back to the LLM
4. Repeat until the conversation is complete or max_turns is reached

In addition to `response.choices[0].message`, there is an additional field `response.choices[0].intermediate_messages`: which contains the list of all messages including tool interactions used. This can be used to continue the conversation with the model.
For more detailed examples of tool calling, check out the `examples/tool_calling_abstraction.ipynb` notebook.

## License

aisuite is released under the MIT License. You are free to use, modify, and distribute the code for both commercial and non-commercial purposes.

## Contributing

If you would like to contribute, please read our [Contributing Guide](https://github.com/andrewyng/aisuite/blob/main/CONTRIBUTING.md) and join our [Discord](https://discord.gg/T6Nvn8ExSb) server!
