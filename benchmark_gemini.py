#!/usr/bin/env python3
"""
Benchmark script for evaluating Gemini 2.5 Pro on SWE-bench tasks
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import argparse
from tqdm import tqdm
from datasets import load_dataset

from router import AIRouter


def create_prompt_for_swebench_task(task: Dict[str, Any]) -> str:
    """Create a prompt for Gemini to solve a SWE-bench task"""
    prompt = f"""You are an expert software engineer. You need to solve the following issue by providing a patch.

Repository: {task['repo']}
Issue: {task['problem_statement']}

Base commit: {task['base_commit']}

Please analyze the issue and provide a complete patch that fixes the problem. The patch should:
1. Be in unified diff format (compatible with git apply)
2. Include all necessary changes to fix the issue
3. Be minimal and focused only on fixing the described problem
4. Not include any test files unless specifically required

Provide ONLY the patch content without any additional explanation.

Example patch:
diff --git a/src/sqlfluff/rules/L031.py b/src/sqlfluff/rules/L031.py
--- a/src/sqlfluff/rules/L031.py
+++ b/src/sqlfluff/rules/L031.py
@@ -211,7 +211,7 @@ def _lint_aliases_in_join(
violation_buff.append(
LintResult(
anchor=alias_info.alias_identifier_ref,
- description="Avoid using aliases in join condition",
+ description="Avoid aliases in from clauses and join conditions.",
fixes=fixes,
)
)
"""
    
    if task.get('hints_text'):
        prompt += f"\n\nHints from issue comments:\n{task['hints_text']}"
    
    return prompt


def generate_prediction_with_gemini(router: AIRouter, task: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a prediction for a single SWE-bench task using Gemini directly"""
    prompt = create_prompt_for_swebench_task(task)
    
    messages = [{"role": "user", "content": prompt}]
    
    try:
        # Call Gemini directly
        response = router.call_gemini(messages, max_tokens=4000, temperature=0.1)
        
        # Extract the response
        prediction = response.choices[0].message.content
        
        # Create prediction entry
        prediction_entry = {
            "instance_id": task["instance_id"],
            "model_name_or_path": "gemini-2.5-pro",
            "model_patch": prediction
        }
        
        return prediction_entry
        
    except Exception as e:
        print(f"Error processing task {task['instance_id']}: {str(e)}")
        return {
            "instance_id": task["instance_id"],
            "model_name_or_path": "gemini-2.5-pro",
            "model_patch": "",  # Empty patch on error
            "error": str(e)
        }


def benchmark_gemini(
    dataset_name: str = "princeton-nlp/SWE-bench_Lite",
    output_file: str = None,
    limit: int = None,
    start_idx: int = 0
):
    """Run benchmark on SWE-bench using Gemini 2.5 Pro directly"""
    
    # Initialize router
    print("Initializing AI Router with Gemini 2.5 Pro...")
    
    # Configure with Google API key
    config = {
        "google": {"api_key": os.getenv("GOOGLE_API_KEY")}
    }
    
    if not config["google"]["api_key"]:
        print("Error: GOOGLE_API_KEY environment variable not set!")
        sys.exit(1)
    
    router = AIRouter(config=config)
    
    # Load dataset
    print(f"Loading dataset: {dataset_name}")
    dataset = load_dataset(dataset_name, split="test")
    
    # Apply limit if specified
    if limit:
        if limit == 1:
            # For single item test, use index 10 like in original
            dataset = dataset.select(range(start_idx+10, start_idx + 11))
        else:
            dataset = dataset.select(range(start_idx, min(start_idx + limit, len(dataset))))
    
    # Prepare output file
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"predictions_gemini_{timestamp}.jsonl"
    
    output_path = Path(output_file)
    
    # Load existing predictions if resuming
    existing_predictions = set()
    if output_path.exists() and start_idx > 0:
        with open(output_path, 'r') as f:
            for line in f:
                pred = json.loads(line)
                existing_predictions.add(pred['instance_id'])
    
    print(f"Starting benchmark from index {start_idx}")
    print(f"Output will be saved to: {output_file}")
    print(f"Total tasks to process: {len(dataset)}")
    print("=" * 80)
    
    # Process tasks
    with open(output_path, 'a' if start_idx > 0 else 'w') as f:
        for idx in tqdm(range(start_idx, len(dataset)), desc="Processing tasks"):
            task = dataset[idx]
            
            # Skip if already processed
            if task['instance_id'] in existing_predictions:
                print(f"Skipping already processed: {task['instance_id']}")
                continue
            
            print(f"\nProcessing [{idx+1}/{len(dataset)}]: {task['instance_id']}")
            print(f"Repository: {task['repo']}")
            
            # Generate prediction
            prediction = generate_prediction_with_gemini(router, task)
            
            # Write to file immediately
            f.write(json.dumps(prediction) + '\n')
            f.flush()
            
            # Print summary
            if not prediction.get('error'):
                print(f"✓ Generated prediction for: {prediction['instance_id']}")
                if prediction['model_patch']:
                    print(f"  Patch length: {len(prediction['model_patch'])} characters")
            else:
                print(f"✗ Error: {prediction['error']}")
    
    print(f"\nBenchmark complete! Predictions saved to: {output_file}")
    return output_file


def validate_predictions(predictions_file: str):
    """Validate that predictions file is in correct format"""
    print(f"\nValidating predictions file: {predictions_file}")
    
    valid_count = 0
    error_count = 0
    empty_count = 0
    
    with open(predictions_file, 'r') as f:
        for line_no, line in enumerate(f, 1):
            try:
                pred = json.loads(line)
                
                # Check required fields
                assert 'instance_id' in pred, "Missing instance_id"
                assert 'model_name_or_path' in pred, "Missing model_name_or_path"
                assert 'model_patch' in pred, "Missing model_patch"
                
                if pred.get('error'):
                    error_count += 1
                elif not pred['model_patch'].strip():
                    empty_count += 1
                else:
                    valid_count += 1
                    
            except Exception as e:
                print(f"  Line {line_no}: Invalid JSON or missing fields - {e}")
    
    total = valid_count + error_count + empty_count
    print(f"\nValidation Summary:")
    print(f"  Total predictions: {total}")
    print(f"  Valid predictions: {valid_count}")
    print(f"  Empty predictions: {empty_count}")
    print(f"  Error predictions: {error_count}")
    
    return valid_count > 0


def main():
    parser = argparse.ArgumentParser(description="Benchmark Gemini 2.5 Pro on SWE-bench")
    parser.add_argument("--dataset", default="princeton-nlp/SWE-bench_Lite", 
                       help="Dataset name (default: princeton-nlp/SWE-bench_Lite)")
    parser.add_argument("--output", help="Output file path (default: auto-generated)")
    parser.add_argument("--limit", type=int, help="Limit number of tasks to process", default=20)
    parser.add_argument("--start-idx", type=int, default=0, 
                       help="Start from this index (for resuming)")
    parser.add_argument("--validate-only", help="Only validate existing predictions file")
    
    args = parser.parse_args()
    
    if args.validate_only:
        # Just validate existing predictions
        if validate_predictions(args.validate_only):
            print("\n✓ Predictions file is valid and ready for evaluation!")
        else:
            print("\n✗ Predictions file has issues!")
    else:
        # Run benchmark
        predictions_file = benchmark_gemini(
            dataset_name=args.dataset,
            output_file=args.output,
            limit=args.limit,
            start_idx=args.start_idx
        )
        
        # Validate generated predictions
        if validate_predictions(predictions_file):
            print("\n✓ Predictions are ready for SWE-bench evaluation!")
            print(f"\nTo run evaluation, use:")
            print(f"  python -m swebench.harness.run_evaluation \\")
            print(f"    --dataset_name {args.dataset} \\")
            print(f"    --predictions_path {predictions_file} \\")
            print(f"    --max_workers 8 \\")
            print(f"    --run_id gemini_eval")


if __name__ == "__main__":
    main()