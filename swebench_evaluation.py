#!/usr/bin/env python3
"""
SWE-bench evaluation wrapper for parallelsynthetize_route

NOTE: Before running the evaluation, ensure:
1. Docker is installed and running
2. Your user is in the docker group: sudo usermod -aG docker $USER
3. Log out and back in for group changes to take effect
"""

import json
import os
from typing import List, Dict, Any
from datasets import load_dataset
from router import AIRouter
from dotenv import load_dotenv
import argparse
from tqdm import tqdm

# Load environment variables
load_dotenv()

def create_swebench_prompt(instance: Dict[str, Any]) -> str:
    """Create a prompt for solving a SWE-bench instance"""
    prompt = f"""You are tasked with solving a software engineering issue in a repository.

Repository: {instance['repo']}
Issue: {instance['problem_statement']}

Base commit: {instance['base_commit']}

Please analyze the issue and provide a patch that fixes the problem. The patch should be in unified diff format (like the output of `git diff`).

Your response should contain ONLY the patch, starting with the diff header. Do not include any explanations or additional text."""
    
    return prompt

def generate_predictions(router: AIRouter, dataset, output_file: str, max_instances: int = None):
    """Generate predictions for SWE-bench instances using parallelsynthetize_route"""
    predictions = []
    
    # Limit instances if specified
    instances = list(dataset)
    if max_instances:
        instances = instances[:max_instances]
    
    for instance in tqdm(instances, desc="Generating predictions"):
        try:
            # Create prompt for this instance
            prompt = create_swebench_prompt(instance)
            
            # Create messages format expected by the router
            messages = [{"role": "user", "content": prompt}]
            
            # Use parallelsynthetize_route to get synthesized response
            response, metadata = router.parallelsynthetize_route(messages, max_tokens=4000)
            
            # Extract the response content
            prediction_text = response.choices[0].message.content
            
            # Create prediction entry
            prediction = {
                "instance_id": instance["instance_id"],
                "model": "parallelsynthetize_route",
                "prediction": prediction_text
            }
            
            predictions.append(prediction)
            
            # Save predictions incrementally
            with open(output_file, 'w') as f:
                for pred in predictions:
                    f.write(json.dumps(pred) + '\n')
            
            print(f"\nProcessed {instance['instance_id']}")
            print(f"Models used: {metadata.get('models_used', [])}")
            print(f"Best individual model: {metadata.get('best_individual_model', 'N/A')}")
            
        except Exception as e:
            print(f"\nError processing {instance['instance_id']}: {str(e)}")
            # Add empty prediction for failed instances
            prediction = {
                "instance_id": instance["instance_id"],
                "model": "parallelsynthetize_route",
                "prediction": ""
            }
            predictions.append(prediction)
    
    return predictions

def validate_gold_predictions():
    """Validate evaluation setup with gold predictions"""
    print("\nValidating SWE-bench setup with gold predictions...")
    import subprocess
    
    # Set up environment with SWE-bench path
    env = os.environ.copy()
    swebench_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SWE-bench")
    env["PYTHONPATH"] = f"{swebench_path}:{env.get('PYTHONPATH', '')}"
    
    cmd = [
        "python3", "-m", "swebench.harness.run_evaluation",
        "--max_workers", "1",
        "--instance_ids", "sympy__sympy-20590",
        "--predictions_path", "gold",
        "--run_id", "validate-gold"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            print("✓ Gold validation successful!")
            return True
        else:
            print("✗ Gold validation failed!")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Failed to run validation: {str(e)}")
        return False

def run_evaluation(predictions_file: str, run_id: str, max_workers: int = 4):
    """Run SWE-bench evaluation on predictions"""
    print(f"\nRunning SWE-bench evaluation...")
    print(f"Predictions file: {predictions_file}")
    print(f"Run ID: {run_id}")
    print(f"Max workers: {max_workers}")
    
    import subprocess
    
    # Set up environment with SWE-bench path
    env = os.environ.copy()
    swebench_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SWE-bench")
    env["PYTHONPATH"] = f"{swebench_path}:{env.get('PYTHONPATH', '')}"
    
    cmd = [
        "python3", "-m", "swebench.harness.run_evaluation",
        "--dataset_name", "princeton-nlp/SWE-bench_Lite",
        "--predictions_path", predictions_file,
        "--max_workers", str(max_workers),
        "--run_id", run_id
    ]
    
    try:
        # Run evaluation
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        
        # Stream output
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode == 0:
            print("\n✓ Evaluation completed successfully!")
            return True
        else:
            print(f"\n✗ Evaluation failed with code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n✗ Failed to run evaluation: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Evaluate parallelsynthetize_route on SWE-bench")
    parser.add_argument("--dataset", default="princeton-nlp/SWE-bench_Lite", help="Dataset to use")
    parser.add_argument("--split", default="test", help="Dataset split")
    parser.add_argument("--output", default="predictions.jsonl", help="Output file for predictions")
    parser.add_argument("--max-instances", type=int, help="Maximum number of instances to process")
    parser.add_argument("--validate-only", action="store_true", help="Only validate setup with gold predictions")
    parser.add_argument("--evaluate-only", action="store_true", help="Only run evaluation on existing predictions")
    parser.add_argument("--run-id", default="parallelsynthetize_eval", help="Run ID for evaluation")
    parser.add_argument("--max-workers", type=int, default=4, help="Max workers for evaluation")
    args = parser.parse_args()
    
    # Check Docker access
    import subprocess
    try:
        subprocess.run(["docker", "ps"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("Error: Cannot access Docker. Please ensure:")
        print("1. Docker is installed and running")
        print("2. Your user is in the docker group: sudo usermod -aG docker $USER")
        print("3. Log out and back in for group changes to take effect")
        return
    
    if args.validate_only:
        validate_gold_predictions()
        return
    
    if args.evaluate_only:
        if not os.path.exists(args.output):
            print(f"Error: Predictions file not found: {args.output}")
            return
        run_evaluation(args.output, args.run_id, args.max_workers)
        return
    
    print(f"Loading dataset: {args.dataset} (split: {args.split})")
    dataset = load_dataset(args.dataset, split=args.split)
    
    print(f"Dataset loaded with {len(dataset)} instances")
    
    # Initialize router with configuration
    config = {
        "openai": {"api_key": os.getenv("OPENAI_API_KEY")},
        "anthropic": {"api_key": os.getenv("ANTHROPIC_API_KEY")},
        "xai": {"api_key": os.getenv("XAI_API_KEY")},
        "google": {"api_key": os.getenv("GOOGLE_API_KEY")},
    }
    
    # Check for required API keys
    missing_keys = []
    if not config["openai"]["api_key"]:
        missing_keys.append("OPENAI_API_KEY")
    if not config["anthropic"]["api_key"]:
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if missing_keys:
        print(f"Error: Missing required API keys: {', '.join(missing_keys)}")
        print("Please set these environment variables in your .env file")
        return
    
    print("Initializing AI Router...")
    router = AIRouter(config)
    
    print(f"Generating predictions using parallelsynthetize_route...")
    predictions = generate_predictions(router, dataset, args.output, args.max_instances)
    
    print(f"\nCompleted! Generated {len(predictions)} predictions")
    print(f"Predictions saved to: {args.output}")
    
    # Print summary
    successful = sum(1 for p in predictions if p["prediction"])
    print(f"Successful predictions: {successful}/{len(predictions)}")
    
    # Ask if user wants to run evaluation
    if successful > 0:
        print("\nWould you like to run the SWE-bench evaluation now? (y/n): ", end='')
        if input().lower() == 'y':
            run_evaluation(args.output, args.run_id, args.max_workers)

if __name__ == "__main__":
    main()