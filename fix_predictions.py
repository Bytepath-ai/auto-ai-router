#!/usr/bin/env python3
"""Fix predictions format for SWE-bench evaluation"""

import json

# Read predictions
predictions = []
with open('predictions.jsonl', 'r') as f:
    for line in f:
        pred = json.loads(line)
        # Update the format - rename 'model' to 'model_name_or_path'
        pred['model_name_or_path'] = pred.pop('model')
        
        # Clean up the prediction - remove markdown code fences if present
        prediction_text = pred['prediction']
        if prediction_text.startswith('```diff'):
            prediction_text = prediction_text[7:]  # Remove ```diff
        if prediction_text.endswith('```'):
            prediction_text = prediction_text[:-3]  # Remove trailing ```
        pred['prediction'] = prediction_text.strip()
        
        predictions.append(pred)

# Write fixed predictions
with open('predictions_fixed.jsonl', 'w') as f:
    for pred in predictions:
        f.write(json.dumps(pred) + '\n')

print(f"Fixed {len(predictions)} predictions")
print("Saved to predictions_fixed.jsonl")