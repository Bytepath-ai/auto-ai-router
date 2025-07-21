#!/usr/bin/env python3
import sys
import os

# Add astropy_repo to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'astropy_repo'))

try:
    import numpy as np
    from astropy.nddata import NDDataRef
    
    print("Testing NDDataRef mask propagation issue...")
    
    # Create test data
    array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])
    
    # Create NDDataRef objects
    nref_nomask = NDDataRef(array)
    nref_mask = NDDataRef(array, mask=mask)
    
    print("\nnref_nomask.mask:", nref_nomask.mask)
    print("nref_mask.mask:", nref_mask.mask)
    
    # Test case that should fail: multiply mask by constant
    print("\nTesting: nref_mask.multiply(1., handle_mask=np.bitwise_or)")
    try:
        result = nref_mask.multiply(1., handle_mask=np.bitwise_or)
        print("Result mask:", result.mask)
    except Exception as e:
        print("ERROR:", type(e).__name__, "-", str(e))
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print("Import error:", e)
    print("Make sure you're running this from the playground directory")