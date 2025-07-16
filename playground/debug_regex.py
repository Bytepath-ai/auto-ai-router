#!/usr/bin/env python3
import re

# The exact regex from the code
_decimal_re = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
_command_re = r"READ [TS]ERR(\s+[0-9]+)+"

delimiter = None
sep = r"\s+" if delimiter is None else delimiter
_new_re = rf"NO({sep}NO)+"
_data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*)"
_type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"

print("Full regex pattern:")
print(_type_re)
print("\nCommand regex:")
print(_command_re)

# Test with and without IGNORECASE
pattern_with_ignore = re.compile(_type_re, re.IGNORECASE)
pattern_without_ignore = re.compile(_type_re)

test_line = "read serr 1 2"

print(f"\nTesting '{test_line}':")
print(f"With IGNORECASE: {bool(pattern_with_ignore.match(test_line))}")
print(f"Without IGNORECASE: {bool(pattern_without_ignore.match(test_line))}")

# Also test the command regex directly
command_pattern_ignore = re.compile(_command_re, re.IGNORECASE)
command_pattern_no_ignore = re.compile(_command_re)

print(f"\nDirect command regex test:")
print(f"With IGNORECASE: {bool(command_pattern_ignore.match(test_line))}")
print(f"Without IGNORECASE: {bool(command_pattern_no_ignore.match(test_line))}")