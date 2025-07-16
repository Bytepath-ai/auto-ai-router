#!/bin/bash
# Script to run SWE-bench evaluation with proper Python path

# Add SWE-bench to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/SWE-bench"

# Check if user wants to validate setup first
if [ "$1" == "--check" ]; then
    echo "Running setup check..."
    python3 test_swebench_setup.py
    exit $?
fi

# Run the evaluation
echo "Running SWE-bench evaluation..."
echo "Python path includes: $PYTHONPATH"

# Pass all arguments to the evaluation script
python3 swebench_evaluation.py "$@"