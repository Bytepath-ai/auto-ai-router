#!/usr/bin/env python3
"""Trace through the QDP parsing to find the issue."""

import re

def _line_type(line, delimiter=None):
    """Simplified version of _line_type from qdp.py"""
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
        raise ValueError(f"Unrecognized QDP line: {line}")
    for type_, val in match.groupdict().items():
        if val is None:
            continue
        if type_ == "data":
            return f"data,{len(val.split(sep=delimiter))}"
        else:
            return type_

# Test the function
test_line = "read serr 1 2"
print(f"Testing line: '{test_line}'")
print(f"Line type: {_line_type(test_line)}")

# Now let's trace what happens in _get_tables_from_qdp_file
command_lines = test_line + "\n"
err_specs = {}

# This is what happens in the parsing code
for cline in command_lines.strip().split("\n"):
    command = cline.strip().split()
    print(f"Command split: {command}")
    if len(command) < 3:
        continue
    err_specs[command[1].lower()] = [int(c) for c in command[2:]]
    
print(f"err_specs: {err_specs}")