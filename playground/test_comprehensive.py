#!/usr/bin/env python
"""Comprehensive test for memoryview handling in HttpResponse."""

import sys
sys.path.insert(0, '/home/burny/josef/auto-ai-router/django_full')

import django
from django.conf import settings

# Configure Django settings
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-secret-key',
    DEFAULT_CHARSET='utf-8',
)
django.setup()

from django.http import HttpResponse, StreamingHttpResponse

print("Testing HttpResponse with memoryview objects...\n")

# Test 1: Basic memoryview in HttpResponse constructor
print("Test 1: HttpResponse with memoryview in constructor")
response = HttpResponse(memoryview(b"Hello World"))
assert response.content == b"Hello World", f"Expected b'Hello World', got {response.content}"
print("✓ Passed")

# Test 2: Setting content property with memoryview
print("\nTest 2: Setting content property with memoryview")
response = HttpResponse()
response.content = memoryview(b"Test Content")
assert response.content == b"Test Content", f"Expected b'Test Content', got {response.content}"
print("✓ Passed")

# Test 3: Writing memoryview content
print("\nTest 3: Writing memoryview content")
response = HttpResponse()
response.write(memoryview(b"Part 1"))
response.write(memoryview(b" Part 2"))
assert response.content == b"Part 1 Part 2", f"Expected b'Part 1 Part 2', got {response.content}"
print("✓ Passed")

# Test 4: Empty memoryview
print("\nTest 4: Empty memoryview")
response = HttpResponse(memoryview(b""))
assert response.content == b"", f"Expected b'', got {response.content}"
print("✓ Passed")

# Test 5: Large memoryview
print("\nTest 5: Large memoryview")
large_data = b"x" * 10000
response = HttpResponse(memoryview(large_data))
assert response.content == large_data, "Large memoryview content mismatch"
print("✓ Passed")

# Test 6: StreamingHttpResponse with memoryview
print("\nTest 6: StreamingHttpResponse with memoryview")
response = StreamingHttpResponse([memoryview(b"Stream"), memoryview(b" Data")])
content = b''.join(response.streaming_content)
assert content == b"Stream Data", f"Expected b'Stream Data', got {content}"
print("✓ Passed")

# Test 7: Mixed content types
print("\nTest 7: Mixed content types in list")
response = HttpResponse([b"bytes", "string", memoryview(b" memoryview")])
assert response.content == b"bytesstring memoryview", f"Expected b'bytesstring memoryview', got {response.content}"
print("✓ Passed")

# Test 8: Binary data in memoryview
print("\nTest 8: Binary data in memoryview")
binary_data = b"\x00\x01\x02\xFF\xFE\xFD"
response = HttpResponse(memoryview(binary_data))
assert response.content == binary_data, "Binary data mismatch"
print("✓ Passed")

print("\n✅ All tests passed! HttpResponse now correctly handles memoryview objects.")