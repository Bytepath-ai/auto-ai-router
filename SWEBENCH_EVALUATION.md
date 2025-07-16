# SWE-bench Evaluation of parallelsynthetize_route

This guide explains how to evaluate the `parallelsynthetize_route` function from `router.py` using SWE-bench.

## Prerequisites

1. **Docker Setup** (REQUIRED)
   ```bash
   # Install Docker if not already installed
   sudo apt-get update
   sudo apt-get install docker.io
   
   # Add your user to the docker group
   sudo usermod -aG docker $USER
   
   # Log out and back in for group changes to take effect
   # Or use: newgrp docker
   ```

2. **Environment Variables**
   Create a `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   XAI_API_KEY=your_xai_key  # Optional
   GOOGLE_API_KEY=your_google_key  # Optional
   ```

3. **Python Dependencies**
   ```bash
   pip install datasets tqdm python-dotenv
   ```

## How It Works

The `parallelsynthetize_route` function:
1. Calls multiple AI models in parallel (GPT-4o, Claude Opus 4, O3, etc.)
2. Evaluates and scores all responses
3. Synthesizes the best elements from all models into a comprehensive answer

For SWE-bench evaluation:
1. Each SWE-bench task is sent to `parallelsynthetize_route`
2. The synthesized response (a code patch) is saved
3. SWE-bench applies the patches in Docker containers and runs tests

## Running the Evaluation

### Step 1: Validate Setup
First, verify your SWE-bench installation works:
```bash
python3 swebench_evaluation.py --validate-only
```

### Step 2: Generate Predictions
Generate predictions for SWE-bench tasks:
```bash
# For a quick test (5 instances)
python3 swebench_evaluation.py --max-instances 5

# For full SWE-bench Lite dataset (300 instances)
python3 swebench_evaluation.py
```

### Step 3: Run Evaluation
Evaluate the generated predictions:
```bash
python3 swebench_evaluation.py --evaluate-only --run-id my_eval_run
```

## Command Options

- `--dataset`: Dataset to use (default: princeton-nlp/SWE-bench_Lite)
- `--max-instances`: Limit number of instances to process
- `--output`: Output file for predictions (default: predictions.jsonl)
- `--validate-only`: Only validate setup with gold predictions
- `--evaluate-only`: Only run evaluation on existing predictions
- `--run-id`: Unique identifier for the evaluation run
- `--max-workers`: Number of parallel Docker containers (default: 4)

## Expected Output

1. **Predictions File** (`predictions.jsonl`):
   ```json
   {"instance_id": "django__django-11099", "model": "parallelsynthetize_route", "prediction": "diff --git a/..."}
   ```

2. **Evaluation Results** (in `evaluation_results/`):
   - `results.json`: Overall metrics
   - `instance_results.jsonl`: Per-instance results
   - `run_logs/`: Detailed logs for each instance

## Metrics

SWE-bench reports:
- **Resolution Rate**: Percentage of tasks successfully solved
- **Pass@1**: Success rate on first attempt
- **Per-instance Results**: Which tests passed/failed

## Troubleshooting

1. **Docker Permission Denied**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker  # Or log out and back in
   ```

2. **Missing API Keys**
   Ensure your `.env` file contains all required keys

3. **Out of Memory**
   Reduce `--max-workers` to use fewer parallel containers

4. **Slow Performance**
   - The synthesis process calls multiple models, so it's slower than single-model approaches
   - Consider using `--max-instances` for testing

## Cost Considerations

Running parallelsynthetize_route calls multiple models per task:
- GPT-4o (router and synthesis)
- Claude Opus 4
- O3
- GPT-4o-mini
- Grok-4 (if configured)
- Gemini 2.5 Pro (if configured)

Estimate ~$0.10-0.20 per SWE-bench instance depending on prompt length.

## Analysis

After evaluation, analyze results:
```bash
# View overall results
cat evaluation_results/*/results.json | jq .

# Check which models performed best
grep "best_model" predictions.jsonl | sort | uniq -c

# View parallel route statistics
cat parallel_route_stats.txt
```

## Next Steps

1. Compare results with individual model performance
2. Analyze which types of tasks benefit most from synthesis
3. Tune the synthesis prompt for better performance
4. Experiment with different model combinations