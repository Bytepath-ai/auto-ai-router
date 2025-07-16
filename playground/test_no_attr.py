import numpy as np

# Test with object that has no mask attribute
class NoMaskAttr:
    def __init__(self, data):
        self.data = data
        # No mask attribute at all

obj = NoMaskAttr([1, 2, 3])

print("Object with no mask attribute:")
print(f"hasattr(obj, 'mask'): {hasattr(obj, 'mask')}")
print(f"getattr(obj, 'mask', None): {getattr(obj, 'mask', None)}")
print(f"getattr(obj, 'mask', None) is None: {getattr(obj, 'mask', None) is None}")

# Try accessing directly
try:
    print(f"obj.mask: {obj.mask}")
except AttributeError as e:
    print(f"AttributeError when accessing obj.mask: {e}")

# The condition check
print(f"\nCondition check: {getattr(obj, 'mask', None) is None}")

# What happens with bitwise_or
mask = np.array([1, 0, 1])
try:
    result = np.bitwise_or(mask, obj.mask)
except AttributeError as e:
    print(f"AttributeError with bitwise_or: {e}")
except TypeError as e:
    print(f"TypeError with bitwise_or: {e}")