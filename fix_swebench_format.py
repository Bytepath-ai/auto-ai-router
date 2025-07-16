#!/usr/bin/env python3
import json

# Read the predictions file
with open('predictions_fixed.jsonl', 'r') as f:
    predictions = [json.loads(line) for line in f if line.strip()]

# Fix the format by changing 'prediction' to 'model_patch'
fixed_predictions = []
for pred in predictions:
    fixed_pred = {
        'instance_id': pred['instance_id'],
        'model_patch': pred['prediction'],
        'model_name_or_path': pred.get('model_name_or_path', 'parallelsynthetize_route')
    }
    fixed_predictions.append(fixed_pred)

# Write the fixed predictions
with open('predictions_swebench_format.jsonl', 'w') as f:
    for pred in fixed_predictions:
        f.write(json.dumps(pred) + '\n')

print(f"Fixed {len(fixed_predictions)} predictions")
print("Output written to predictions_swebench_format.jsonl")