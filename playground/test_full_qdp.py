#!/usr/bin/env python3
"""Test the full QDP parsing flow"""
import sys
import os
sys.path.insert(0, 'astropy_repo')

from astropy.io.ascii.qdp import _get_lines_from_file, _get_type_from_list_of_lines

# Test content with lowercase commands
test_content = """read serr 1 2
1 0.5 1 0.5
"""

# Get lines
lines = test_content.strip().split('\n')
print(f"Lines: {lines}")

try:
    # Process lines
    types, ncol = _get_type_from_list_of_lines(lines)
    print(f"Types: {types}")
    print(f"Number of columns: {ncol}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()