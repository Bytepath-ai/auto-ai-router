#!/usr/bin/env python3
"""Simple verification that the documentation fix is correct"""

# Let's verify the actual implementation signature
import ast

# Read the implementation file
with open('astropy_repo/astropy/nddata/mixins/ndarithmetic.py', 'r') as f:
    content = f.read()

# Parse the AST
tree = ast.parse(content)

# Find the _arithmetic_meta method
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_arithmetic_meta':
        print("Found _arithmetic_meta method in implementation:")
        print(f"  Line {node.lineno}: def {node.name}(", end="")
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        print(", ".join(args) + ", **kwds)")
        print(f"\nThe third parameter (after self, operation, operand) is: '{args[3]}'")
        
# Now check the documentation
with open('astropy_repo/docs/nddata/subclassing.rst', 'r') as f:
    doc_lines = f.readlines()

print("\nChecking documentation after fix:")
for i, line in enumerate(doc_lines):
    if '_arithmetic_meta(self, operation, operand,' in line:
        print(f"  Line {i+1}: {line.strip()}")
        # Extract the parameter name
        if 'handle_meta' in line:
            print("  ✓ Documentation correctly uses 'handle_meta' parameter")
        elif 'handle_mask' in line:
            print("  ✗ Documentation incorrectly uses 'handle_mask' parameter")