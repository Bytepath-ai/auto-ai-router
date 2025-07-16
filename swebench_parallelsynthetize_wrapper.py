#!/usr/bin/env python3
"""
SWE-bench wrapper for parallelsynthetize_route
Makes the router function compatible with SWE-bench evaluation framework
"""

import os
import json
from typing import List, Dict, Any
from datasets import load_dataset
from router import AIRouter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SWEBenchModel:
    """Wrapper to make parallelsynthetize_route compatible with SWE-bench"""
    
    def __init__(self):
        # Initialize router configuration
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
        
        self.router = AIRouter(config)
        self.model_name = "parallelsynthetize-router"
    
    def generate_patch(self, problem_statement: str, repo_info: str = "") -> str:
        """
        Generate a patch for a given problem statement
        
        Args:
            problem_statement: The issue description from SWE-bench
            repo_info: Additional repository context
            
        Returns:
            A patch string in diff format
        """
        # Construct prompt for patch generation
        prompt = f"""You are tasked with fixing the following issue in a software repository.

Problem Statement:
{problem_statement}

{repo_info if repo_info else ''}

Please provide a patch in unified diff format that fixes this issue. The patch should:
1. Be minimal and focused only on fixing the described issue
2. Follow the existing code style and conventions
3. Include proper error handling if needed
4. Be formatted as a proper git diff

Respond with ONLY the patch in diff format, starting with 'diff --git' and including all necessary context."""

        messages = [{"role": "user", "content": prompt}]
        
        try:
            # Use parallelsynthetize_route to generate the patch
            response, metadata = self.router.parallelsynthetize_route(
                messages, 
                max_tokens=2000,
                temperature=0.2  # Lower temperature for more consistent patches
            )
            
            # Extract the patch from the response
            patch = response.choices[0].message.content
            
            # Ensure the patch starts with 'diff --git'
            if not patch.strip().startswith('diff --git'):
                # Try to extract diff from response if it's embedded
                lines = patch.split('\n')
                diff_start = -1
                for i, line in enumerate(lines):
                    if line.startswith('diff --git'):
                        diff_start = i
                        break
                
                if diff_start >= 0:
                    patch = '\n'.join(lines[diff_start:])
                else:
                    # If no proper diff found, wrap in basic diff format
                    patch = f"diff --git a/file.py b/file.py\n--- a/file.py\n+++ b/file.py\n{patch}"
            
            return patch.strip()
            
        except Exception as e:
            print(f"Error generating patch: {str(e)}")
            return ""
    
    def create_predictions_file(self, 
                              dataset_name: str = "princeton-nlp/SWE-bench_Lite",
                              output_file: str = "parallelsynthetize_predictions.jsonl",
                              max_instances: int = 10):
        """
        Create predictions file for SWE-bench evaluation
        
        Args:
            dataset_name: Name of the SWE-bench dataset to use
            output_file: Path to save predictions
            max_instances: Maximum number of instances to process
        """
        print(f"Loading dataset: {dataset_name}")
        dataset = load_dataset(dataset_name, split='test')
        
        predictions = []
        instances_processed = 0
        
        for instance in dataset:
            if instances_processed >= max_instances:
                break
                
            instance_id = instance['instance_id']
            problem_statement = instance['problem_statement']
            
            print(f"\nProcessing instance: {instance_id}")
            print(f"Problem: {problem_statement[:100]}...")
            
            # Generate patch using parallelsynthetize_route
            patch = self.generate_patch(problem_statement)
            
            if patch:
                prediction = {
                    "instance_id": instance_id,
                    "model": self.model_name,
                    "prediction": patch
                }
                predictions.append(prediction)
                print(f"✓ Generated patch for {instance_id}")
            else:
                print(f"✗ Failed to generate patch for {instance_id}")
            
            instances_processed += 1
        
        # Save predictions to file
        with open(output_file, 'w') as f:
            for pred in predictions:
                f.write(json.dumps(pred) + '\n')
        
        print(f"\nSaved {len(predictions)} predictions to {output_file}")
        return output_file

def run_swebench_evaluation():
    """Run SWE-bench evaluation on parallelsynthetize_route"""
    
    # Create model wrapper
    model = SWEBenchModel()
    
    # Generate predictions
    predictions_file = model.create_predictions_file(
        dataset_name="princeton-nlp/SWE-bench_Lite",
        output_file="parallelsynthetize_predictions.jsonl",
        max_instances=5  # Start with just 5 for testing
    )
    
    # Run evaluation
    print("\nRunning SWE-bench evaluation...")
    print("To evaluate the predictions, run:")
    print(f"python3 -m swebench.harness.run_evaluation \\")
    print(f"    --dataset_name princeton-nlp/SWE-bench_Lite \\")
    print(f"    --predictions_path {predictions_file} \\")
    print(f"    --max_workers 4 \\")
    print(f"    --run_id parallelsynthetize_eval")

if __name__ == "__main__":
    run_swebench_evaluation()