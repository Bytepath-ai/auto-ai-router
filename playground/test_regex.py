#!/usr/bin/env python3
import re

# Test the regex pattern with case sensitivity
_decimal_re = r"[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"
_command_re = r"READ [TS]ERR(\s+[0-9]+)+"
delimiter = None
sep = r"\s+" if delimiter is None else delimiter
_new_re = rf"NO({sep}NO)+"
_data_re = rf"({_decimal_re}|NO|[-+]?nan)({sep}({_decimal_re}|NO|[-+]?nan))*)"
_type_re = rf"^\s*((?P<command>{_command_re})|(?P<new>{_new_re})|(?P<data>{_data_re})?\s*(\!(?P<comment>.*))?\s*$"

# Test with IGNORECASE flag
_line_type_re = re.compile(_type_re, re.IGNORECASE)

test_lines = [
    "READ SERR 1 2",
    "read serr 1 2",
    "Read Serr 1 2",
    "READ TERR 3",
    "read terr 3"
]

for line in test_lines:
    match = _line_type_re.match(line.strip())
    if match:
        groups = match.groupdict()
        if groups.get('command'):
            print(f"'{line}' -> Matched as command")
        else:
            print(f"'{line}' -> Matched but not as command: {[k for k,v in groups.items() if v]}")
    else:
        print(f"'{line}' -> No match!")