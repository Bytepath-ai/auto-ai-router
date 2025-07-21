import numpy as np

# Test the behavior of replace on chararray
arr = np.chararray(5, itemsize=10)
arr[:] = b'1.23E+05'

print("Original array:", arr)

# This doesn't modify arr in-place
arr.replace(b'E', b'D')
print("After arr.replace(b'E', b'D'):", arr)

# This does modify arr in-place
arr[:] = arr.replace(b'E', b'D')
print("After arr[:] = arr.replace(b'E', b'D'):", arr)