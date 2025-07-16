# SWE-bench Evaluation of parallelsynthetize_route

## Overview

I've set up a complete evaluation framework to test the `parallelsynthetize_route` function from `router.py` using SWE-bench. This function:

1. **Calls multiple AI models in parallel**: GPT-4o, Claude Opus 4, O3, GPT-4o-mini, Grok-4, and Gemini 2.5 Pro
2. **Evaluates and scores** all responses using GPT-4o
3. **Synthesizes** the best elements from all models into one comprehensive answer

## Files Created

1. **`swebench_evaluation.py`**: Main evaluation script that:
   - Loads SWE-bench tasks
   - Converts them to prompts for parallelsynthetize_route
   - Collects synthesized responses as predictions
   - Runs the SWE-bench evaluation harness

2. **`test_swebench_setup.py`**: Setup verification script that checks:
   - Python dependencies
   - API keys
   - Docker installation and permissions
   - SWE-bench installation

3. **`run_swebench_eval.sh`**: Wrapper script that:
   - Sets up Python path correctly
   - Provides easy command-line interface

4. **`SWEBENCH_EVALUATION.md`**: Detailed documentation

## How to Run the Evaluation

### Step 1: Fix Docker Permissions (Required)
```bash
# Add yourself to docker group
sudo usermod -aG docker $USER

# Apply changes (choose one):
newgrp docker  # Start new shell with group
# OR
logout and login again
```

### Step 2: Check Setup
```bash
./run_swebench_eval.sh --check
```

### Step 3: Run a Test Evaluation (1 instance)
```bash
./run_swebench_eval.sh --max-instances 1
```

### Step 4: Run Full Evaluation
```bash
# For SWE-bench Lite (300 instances)
./run_swebench_eval.sh

# For specific number of instances
./run_swebench_eval.sh --max-instances 10
```

## Expected Behavior

1. **Prediction Generation**: 
   - Each SWE-bench task is sent to all models in parallel
   - Responses are evaluated and synthesized
   - Progress is shown with model usage statistics

2. **Evaluation Process**:
   - SWE-bench applies the generated patches in Docker containers
   - Runs repository tests to verify fixes
   - Produces detailed results

3. **Output Files**:
   - `predictions.jsonl`: Generated patches
   - `parallel_route_stats.txt`: Statistics on model performance
   - `evaluation_results/`: Full evaluation results

## Key Insights

This evaluation will reveal:
- Whether synthesizing multiple model responses improves patch quality
- Which types of software engineering tasks benefit most from multi-model synthesis
- The computational cost vs. benefit trade-off

## Next Steps

After running the evaluation:
1. Compare results against individual model baselines
2. Analyze the parallel_route_stats.txt to see model selection patterns
3. Review which models contributed most to successful patches
4. Consider optimizations based on findings

## Important Notes

- **Cost**: Each task calls multiple models, expect ~$0.10-0.20 per instance
- **Time**: Synthesis takes longer than single models due to parallel calls
- **Docker**: Required for SWE-bench to create isolated test environments
- **API Keys**: Must have at least OpenAI and Anthropic keys configured