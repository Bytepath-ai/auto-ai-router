class NDDataTest:
    def __init__(self, data, mask=None):
        self.data = data
        self.mask = mask

# Test object with None mask
obj = NDDataTest([1, 2, 3], mask=None)
print(f"obj.mask = {obj.mask}")
print(f"obj.mask is None = {obj.mask is None}")
print(f"getattr(obj, 'mask', None) = {getattr(obj, 'mask', None)}")
print(f"getattr(obj, 'mask', None) is None = {getattr(obj, 'mask', None) is None}")

# Test with no mask attribute at all
class NoMask:
    def __init__(self, data):
        self.data = data

obj2 = NoMask([1, 2, 3])
print(f"\nhasattr(obj2, 'mask') = {hasattr(obj2, 'mask')}")
print(f"getattr(obj2, 'mask', None) = {getattr(obj2, 'mask', None)}")
print(f"getattr(obj2, 'mask', None) is None = {getattr(obj2, 'mask', None) is None}")