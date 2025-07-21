import numpy as np
from astropy.nddata import NDDataRef

# Test case from the issue
array = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])

nref_nomask = NDDataRef(array)
nref_mask = NDDataRef(array, mask=mask)

# This should fail with TypeError: unsupported operand type(s) for |: 'int' and 'NoneType'
try:
    result = nref_mask.multiply(1., handle_mask=np.bitwise_or)
    print("ERROR: Should have failed but didn't!")
except TypeError as e:
    print(f"Got expected error: {e}")

# This should also fail
try:
    result = nref_mask.multiply(nref_nomask, handle_mask=np.bitwise_or)
    print("ERROR: Should have failed but didn't!")
except TypeError as e:
    print(f"Got expected error: {e}")