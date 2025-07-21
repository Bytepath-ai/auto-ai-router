#!/usr/bin/env python3
import re

# Test the character class issue
print("Testing character class with re.IGNORECASE:")
print("="*50)

# Pattern with [TS] - should NOT match lowercase 's' even with IGNORECASE
pattern1 = re.compile(r"READ [TS]ERR", re.IGNORECASE)
test_cases = ["READ SERR", "read serr", "READ TERR", "read terr"]

print("Pattern: r'READ [TS]ERR' with re.IGNORECASE")
for test in test_cases:
    match = pattern1.match(test)
    print(f"  '{test}' -> {'MATCH' if match else 'NO MATCH'}")

print("\n" + "="*50)

# Pattern with [TtSs] - should match all cases
pattern2 = re.compile(r"READ [TtSs]ERR", re.IGNORECASE)
print("Pattern: r'READ [TtSs]ERR' with re.IGNORECASE")
for test in test_cases:
    match = pattern2.match(test)
    print(f"  '{test}' -> {'MATCH' if match else 'NO MATCH'}")

# Additional test to confirm the issue
print("\n" + "="*50)
print("Character class behavior with re.IGNORECASE:")
pattern_char = re.compile(r"[A]", re.IGNORECASE)
print("Pattern [A] with IGNORECASE:")
print(f"  'A' matches: {bool(pattern_char.match('A'))}")
print(f"  'a' matches: {bool(pattern_char.match('a'))}")  # This should be False!

pattern_char2 = re.compile(r"[Aa]", re.IGNORECASE)
print("Pattern [Aa] with IGNORECASE:")
print(f"  'A' matches: {bool(pattern_char2.match('A'))}")
print(f"  'a' matches: {bool(pattern_char2.match('a'))}")