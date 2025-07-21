#!/usr/bin/env python
"""Test the fix for memoryview handling."""

# Simulate the fixed make_bytes method
def make_bytes_fixed(value, charset='utf-8'):
    """Turn a value into a bytestring encoded in the output charset."""
    # Per PEP 3333, this response body must be bytes. To avoid returning
    # an instance of a subclass, this function returns `bytes(value)`.
    # This doesn't make a copy when `value` already contains bytes.

    # Handle string types -- we can't rely on force_bytes here because:
    # - Python attempts str conversion first
    # - when self._charset != 'utf-8' it re-encodes the content
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, str):
        return bytes(value.encode(charset))
    # Handle memoryview objects by converting them to bytes.
    if isinstance(value, memoryview):
        return bytes(value)
    # Handle non-string types.
    return str(value).encode(charset)

# Test the fix
mv = memoryview(b"My Content")
result = make_bytes_fixed(mv)
print(f"Fixed make_bytes(memoryview): {result}")
print(f"Expected: b'My Content'")
print(f"Success: {result == b'My Content'}")