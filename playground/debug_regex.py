#!/usr/bin/env python3
import re

# Test with the exact pattern from the code
_decimal_re = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
_command_re = r"READ [TS]ERR(\s+[0-9]+)+"

sep = r"\s+"
_new_re = rf"NO({sep}NO)+"
_data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*)"

# Build the exact pattern as in the code
_type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"

print("Pattern components:")
print(f"_command_re: {_command_re}")
print(f"_type_re: {_type_re}")
print()

# Test with and without IGNORECASE
pattern_with_ignore = re.compile(_type_re, re.IGNORECASE)
pattern_without_ignore = re.compile(_type_re)

test_line = "read serr 1 2"
print(f"Testing: '{test_line}'")

# With IGNORECASE
match = pattern_with_ignore.match(test_line.strip())
print(f"With IGNORECASE: {match is not None}")
if match:
    print(f"  Matched: {match.group(0)}")

# Without IGNORECASE  
match = pattern_without_ignore.match(test_line.strip())
print(f"Without IGNORECASE: {match is not None}")

# Let's also check what happens with the closing parenthesis
print("\nChecking pattern details...")
print(f"Does _type_re have unmatched parentheses? Let's count:")
print(f"Opening parens: {_type_re.count('(')}")
print(f"Closing parens: {_type_re.count(')')}")