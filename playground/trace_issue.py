#!/usr/bin/env python
"""Trace through the HttpResponse code to understand the issue."""

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

from django.http.response import HttpResponse

# Check the content setter
print("Testing HttpResponse content setter behavior...")

# Create response with memoryview
mv = memoryview(b"My Content")
response = HttpResponse()

# Trace through the content setter
print(f"\nOriginal memoryview: {mv}")
print(f"bytes(memoryview): {bytes(mv)}")

# Set content and check
response.content = mv
print(f"\nAfter setting content:")
print(f"response._container: {response._container}")
print(f"response.content: {response.content}")

# Check if it's using the iterator path
print(f"\nChecking if memoryview has __iter__: {hasattr(mv, '__iter__')}")
print(f"Is memoryview instance of (bytes, str)?: {isinstance(mv, (bytes, str))}")

# Test the make_bytes method directly
print(f"\nDirect make_bytes test:")
print(f"response.make_bytes(mv): {response.make_bytes(mv)}")