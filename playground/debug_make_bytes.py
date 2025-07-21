#!/usr/bin/env python
"""Debug the make_bytes behavior."""

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

from django.http import HttpResponse

# Create a test response instance to access make_bytes
response = HttpResponse()

# Test make_bytes with different inputs
mv = memoryview(b"My Content")

print(f"Original memoryview: {mv}")
print(f"bytes(memoryview): {bytes(mv)}")
print(f"str(memoryview): {str(mv)}")
print(f"str(memoryview).encode('utf-8'): {str(mv).encode('utf-8')}")

# Call make_bytes
result = response.make_bytes(mv)
print(f"make_bytes(memoryview): {result}")
print(f"make_bytes result type: {type(result)}")

# Decode to see what's in there
print(f"Decoded result (first 50 chars): {result[:50]}")