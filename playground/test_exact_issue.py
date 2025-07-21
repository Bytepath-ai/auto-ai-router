#!/usr/bin/env python3
import re

# Let's test the exact scenario from the issue
def _line_type(line, delimiter=None):
    """Exact copy of the function from qdp.py"""
    _decimal_re = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
    _command_re = r"READ [TS]ERR(\s+[0-9]+)+"

    sep = delimiter
    if delimiter is None:
        sep = r"\s+"
    _new_re = rf"NO({sep}NO)+"
    _data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*)"
    _type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"
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

# Test with the exact input from the issue
print("Testing the exact scenario from the issue:")
test_lines = [
    "read serr 1 2 ",  # Note the trailing space in the issue
    "1 0.5 1 0.5"
]

for i, line in enumerate(test_lines):
    print(f"\nLine {i}: '{line}'")
    try:
        result = _line_type(line)
        print(f"  Result: {result}")
    except ValueError as e:
        print(f"  Error: {e}")

# Additional test with exact characters
print("\n\nChecking character codes:")
test = "read serr 1 2 "
print(f"String: '{test}'")
print(f"Stripped: '{test.strip()}'")
print(f"Character codes: {[ord(c) for c in test]}")

# Check if there are any hidden characters
import unicodedata
for i, char in enumerate(test):
    name = unicodedata.name(char, f'UNKNOWN (code {ord(char)})')
    print(f"  {i}: '{char}' -> {name}")