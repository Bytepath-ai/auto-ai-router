#!/usr/bin/env python
"""Test script to verify the QDP case sensitivity issue"""

import sys
import tempfile
from astropy.table import Table

# Create test QDP file with lowercase commands
test_content = """read serr 1 2
1 0.5 1 0.5
"""

# Write to temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.qdp', delete=False) as f:
    f.write(test_content)
    temp_file = f.name

print(f"Created test file: {temp_file}")
print(f"Content:\n{test_content}")

try:
    # Try to read the file
    table = Table.read(temp_file, format='ascii.qdp')
    print("SUCCESS: File read successfully!")
    print(table)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    sys.exit(1)