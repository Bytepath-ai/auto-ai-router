import numpy as np

# Simulate the conditions in _arithmetic_mask
class MockOperand:
    def __init__(self, mask=None):
        self.mask = mask

# Test case 1: operand with None mask
self_mask = np.array([[0, 1, 64], [8, 0, 1], [2, 1, 0]])
operand = MockOperand(mask=None)

print("Test 1: operand.mask is None")
print(f"operand is None: {operand is None}")
print(f"getattr(operand, 'mask', None): {getattr(operand, 'mask', None)}")
print(f"getattr(operand, 'mask', None) is None: {getattr(operand, 'mask', None) is None}")
print(f"Condition (operand is None or getattr(operand, 'mask', None) is None): {operand is None or getattr(operand, 'mask', None) is None}")

# What would happen if we didn't check
print("\nWhat happens without the check:")
try:
    result = np.bitwise_or(self_mask, operand.mask)
except TypeError as e:
    print(f"Error: {e}")

# Test with actual values
print("\nTest with actual masks:")
mask1 = np.array([1, 0, 1])
mask2 = np.array([0, 1, 1])
print(f"np.bitwise_or({mask1}, {mask2}) = {np.bitwise_or(mask1, mask2)}")