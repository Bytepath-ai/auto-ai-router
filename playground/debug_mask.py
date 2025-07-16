import numpy as np

# Test what happens with bitwise_or
mask1 = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])
mask2 = None

print("Testing np.bitwise_or with None...")
try:
    result = np.bitwise_or(mask1, mask2)
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

# Check what getattr does
class TestObj:
    def __init__(self):
        self.mask = None

obj = TestObj()
print(f"\ngetattr(obj, 'mask', None) = {getattr(obj, 'mask', None)}")
print(f"obj.mask is None: {obj.mask is None}")
print(f"getattr(obj, 'mask', None) is None: {getattr(obj, 'mask', None) is None}")