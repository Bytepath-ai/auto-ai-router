#!/usr/bin/env python3
"""Fix predictions file format for SWE-bench evaluation."""
import json

# Read the predictions file
with open('predictions_fixed.jsonl', 'r') as f:
    predictions = []
    for line in f:
        if line.strip():
            pred = json.loads(line)
            # Rename 'prediction' to 'model_patch'
            if 'prediction' in pred:
                pred['model_patch'] = pred.pop('prediction')
            predictions.append(pred)

# Write the corrected predictions
with open('predictions_swebench_format.jsonl', 'w') as f:
    for pred in predictions:
        f.write(json.dumps(pred) + '\n')

print(f"Fixed {len(predictions)} predictions")
print("Output written to: predictions_swebench_format.jsonl")