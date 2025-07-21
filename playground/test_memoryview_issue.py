#!/usr/bin/env python
"""Test script to reproduce the memoryview issue in HttpResponse."""

import sys
import os
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

# Test with string content
response = HttpResponse("My Content")
print("String content:", response.content)
assert response.content == b'My Content'

# Test with bytes content
response = HttpResponse(b"My Content")
print("Bytes content:", response.content)
assert response.content == b'My Content'

# Test with memoryview content
response = HttpResponse(memoryview(b"My Content"))
print("Memoryview content:", response.content)
print("Expected: b'My Content'")

# Debug what's happening
mv = memoryview(b"My Content")
print(f"memoryview object: {mv}")
print(f"str(memoryview): {str(mv)}")

# Check if the issue exists
if response.content != b'My Content':
    print("ERROR: HttpResponse doesn't handle memoryview objects correctly!")
    print(f"Got: {response.content}")
    print(f"Expected: b'My Content'")
else:
    print("SUCCESS: HttpResponse handles memoryview objects correctly!")