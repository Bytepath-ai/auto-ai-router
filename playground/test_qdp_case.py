#!/usr/bin/env python
"""Test script to reproduce the QDP case sensitivity issue."""

from astropy.table import Table
import tempfile
import os

# Create a test QDP file with lowercase commands
test_content = """read serr 1 2 
1 0.5 1 0.5
"""

# Write to temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.qdp', delete=False) as f:
    f.write(test_content)
    temp_file = f.name

try:
    # Try to read the file
    print("Attempting to read QDP file with lowercase 'read serr'...")
    table = Table.read(temp_file, format='ascii.qdp')
    print("Success! Table read successfully.")
    print(table)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
finally:
    # Clean up
    os.unlink(temp_file)