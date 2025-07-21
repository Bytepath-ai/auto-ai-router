import numpy as np

class MockNDData:
    def __init__(self, data, mask=None):
        self.data = data
        self.mask = mask

# Test the conditions in _arithmetic_mask
self_obj = MockNDData([1, 2, 3], mask=np.array([0, 1, 0]))
operand_obj = MockNDData([4, 5, 6], mask=None)

print("self_obj.mask:", self_obj.mask)
print("operand_obj.mask:", operand_obj.mask)

# Check the condition
print("\nChecking conditions:")
print("operand_obj is None:", operand_obj is None)
print("getattr(operand_obj, 'mask', None):", getattr(operand_obj, 'mask', None))
print("getattr(operand_obj, 'mask', None) is None:", getattr(operand_obj, 'mask', None) is None)

# The problematic condition
condition = operand_obj is None or getattr(operand_obj, 'mask', None) is None
print("\nCondition result:", condition)

# What happens with bitwise_or
try:
    result = np.bitwise_or(self_obj.mask, operand_obj.mask)
    print("\nbitwise_or result:", result)
except TypeError as e:
    print("\nbitwise_or error:", e)