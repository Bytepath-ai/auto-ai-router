#!/usr/bin/env python3
import re

# Test the current pattern
_command_re = r"READ [TS]ERR(\s+[0-9]+)+"
_decimal_re = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
_new_re = r"NO(\s+NO)+"
_data_re = rf"({_decimal_re}|NO|[-+]?nan)(\s+({_decimal_re}|NO|[-+]?nan))*)"
_type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"

_line_type_re = re.compile(_type_re, re.IGNORECASE)

# Test cases
test_lines = [
    "READ SERR 1 2",    # uppercase
    "read serr 1 2",    # lowercase
    "Read Serr 1 2",    # mixed case
    "READ TERR 1",      # uppercase TERR
    "read terr 1",      # lowercase TERR
]

for line in test_lines:
    match = _line_type_re.match(line.strip())
    if match:
        print(f"'{line}' -> MATCHED")
        print(f"  Groups: {match.groupdict()}")
    else:
        print(f"'{line}' -> NOT MATCHED")