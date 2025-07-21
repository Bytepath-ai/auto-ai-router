#!/usr/bin/env python3
"""Test the complete QDP reading flow by directly using the functions"""
import re

# Copy the exact _line_type function
def _line_type(line, delimiter=None):
    _decimal_re = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
    _command_re = r"READ [TS]ERR(\s+[0-9]+)+"
    
    sep = delimiter
    if delimiter is None:
        sep = r"\s+"
    _new_re = rf"NO({sep}NO)+"
    _data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*)"
    _type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"
    
    print(f"DEBUG: Pattern is: {_type_re}")
    print(f"DEBUG: Testing line: '{line}'")
    
    _line_type_re = re.compile(_type_re, re.IGNORECASE)
    line = line.strip()
    if not line:
        return "comment"
    match = _line_type_re.match(line)
    
    if match is None:
        raise ValueError(f'Unrecognized QDP line: {line}')
    for type_, val in match.groupdict().items():
        if val is None:
            continue
        if type_ == "data":
            return f"data,{len(val.split(sep=delimiter))}"
        else:
            return type_

# Test the problematic line
print("="*60)
print("Testing lowercase command:")
try:
    result = _line_type("read serr 1 2")
    print(f"SUCCESS: Result = {result}")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "="*60)
print("Testing uppercase command:")
try:
    result = _line_type("READ SERR 1 2")
    print(f"SUCCESS: Result = {result}")
except Exception as e:
    print(f"FAILED: {e}")

# Now let's check if there's something specific about the pattern matching
print("\n" + "="*60)
print("Direct regex test:")
_command_re = r"READ [TS]ERR(\s+[0-9]+)+"
pattern = re.compile(_command_re, re.IGNORECASE)
test_str = "read serr 1 2"
match = pattern.match(test_str)
print(f"Pattern: {_command_re}")
print(f"Test string: '{test_str}'")
print(f"Match result: {match}")
if match:
    print(f"Matched: '{match.group(0)}'")