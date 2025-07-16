#!/usr/bin/env python3
"""Fix predictions file to use 'model_patch' key instead of 'prediction'"""

import json

input_file = "predictions_fixed.jsonl"
output_file = "predictions_swebench_ready.jsonl"

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
        if line.strip():
            data = json.loads(line)
            # Rename 'prediction' to 'model_patch'
            if 'prediction' in data:
                data['model_patch'] = data.pop('prediction')
            f_out.write(json.dumps(data) + '\n')

print(f"Created {output_file} with correct key names")