#!/usr/bin/env python
"""Verify how memoryview iteration works."""

mv = memoryview(b"My Content")

print("Iterating over memoryview:")
for i, chunk in enumerate(mv):
    print(f"  chunk {i}: {chunk} (type: {type(chunk)})")
    if i >= 5:  # Just show first few
        print("  ...")
        break

print(f"\nJoining with make_bytes simulation:")
# Simulate what happens in the content setter
chunks = []
for chunk in mv:
    # This is what str(77).encode() would produce
    chunk_bytes = str(chunk).encode('utf-8')
    chunks.append(chunk_bytes)
    print(f"  {chunk} -> {chunk_bytes}")
    if len(chunks) >= 5:
        print("  ...")
        break

result = b''.join(str(chunk).encode('utf-8') for chunk in mv)
print(f"\nFinal result: {result}")