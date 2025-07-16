import sys
sys.path.insert(0, '/home/burny/josef/auto-ai-router/playground/astropy')

import numpy as np
from astropy.nddata import NDDataRef

# Test the issue
array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])

nref_nomask = NDDataRef(array)
nref_mask = NDDataRef(array, mask=mask)

print("Testing mask * no mask scenario...")
try:
    result = nref_mask.multiply(1., handle_mask=np.bitwise_or)
    print("ERROR: This should have failed but didn't!")
except TypeError as e:
    print(f"Got expected TypeError: {e}")
    
print("\nTesting mask * no mask with NDDataRef...")
try:
    result = nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or)
    print("ERROR: This should have failed but didn't!")
except TypeError as e:
    print(f"Got expected TypeError: {e}")