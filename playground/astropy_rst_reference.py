# Reference implementation based on astropy's typical structure
# This shows where to find and how to implement header_rows in RST class

# Typical location: astropy/io/ascii/rst.py

"""
The RST class in astropy is typically defined in astropy/io/ascii/rst.py
Here's the typical structure and where to add header_rows support:
"""

# Example of typical RST class structure:
class RST:
    """
    reStructuredText simple table writer.
    
    Example:
    ========= ======== ====
      Col1     Col2     Col3
    ========= ======== ====
      1.2      "hello"  1
      2.4      's worlds' 2
    ========= ======== ====
    """
    
    def __init__(self):
        # Current implementation typically doesn't have header_rows parameter
        self.header_start = 0
        self.data_start = None
        self.write_comment = False
        self.comment = ''
        self.data_end = None
        
    def write(self, lines):
        """Write header and data lines to create RST table"""
        # Current implementation
        pass

# Example of how FixedWidth implements header_rows:
# Typical location: astropy/io/ascii/fixedwidth.py

class FixedWidth:
    """
    Fixed width table with specified column widths.
    """
    
    def __init__(self, col_starts=None, col_ends=None, delimiter_pad=' ', bookend=True,
                 header_rows=None):  # <-- header_rows parameter
        self.col_starts = col_starts
        self.col_ends = col_ends
        self.delimiter_pad = delimiter_pad
        self.bookend = bookend
        self.header_rows = header_rows  # Store the parameter
        
    def get_fixedwidth_params(self, lines):
        """Get parameters for fixed width table"""
        if self.header_rows:
            # Use specified number of header rows
            header_lines = lines[:self.header_rows]
            # Process header_lines...
        else:
            # Auto-detect header rows
            pass

# How to add header_rows to RST class:

class RST_Modified:
    """
    Modified RST class with header_rows support
    """
    
    def __init__(self, header_rows=None):
        """
        Parameters
        ----------
        header_rows : int, optional
            Number of rows to treat as header rows. If not specified,
            header rows are auto-detected.
        """
        self.header_start = 0
        self.data_start = None
        self.write_comment = False
        self.comment = ''
        self.data_end = None
        self.header_rows = header_rows  # Add this parameter
        
    def read(self, lines):
        """Read RST table from lines"""
        # Find table structure
        delim_lines = []
        for i, line in enumerate(lines):
            if set(line.strip()) <= set('= '):  # RST delimiter line
                delim_lines.append(i)
        
        if self.header_rows is not None:
            # Use specified header_rows
            if len(delim_lines) >= 2:
                # Typical RST structure: delimiter, headers, delimiter, data, delimiter
                self.header_start = delim_lines[0] + 1
                self.header_end = self.header_start + self.header_rows - 1
                self.data_start = delim_lines[1] + 1
                if len(delim_lines) > 2:
                    self.data_end = delim_lines[2]
        else:
            # Auto-detect (current behavior)
            if len(delim_lines) >= 2:
                self.header_start = delim_lines[0] + 1
                self.data_start = delim_lines[1] + 1
                if len(delim_lines) > 2:
                    self.data_end = delim_lines[2]

# Directory structure in astropy:
"""
astropy/
├── io/
│   ├── ascii/
│   │   ├── __init__.py
│   │   ├── core.py          # Base classes
│   │   ├── rst.py           # RST implementation
│   │   ├── fixedwidth.py    # FixedWidth implementation (has header_rows)
│   │   ├── basic.py         # Basic readers/writers
│   │   ├── ui.py            # User interface functions
│   │   └── tests/
│   │       ├── test_rst.py
│   │       └── test_fixedwidth.py
"""

# Key files to modify:
"""
1. astropy/io/ascii/rst.py
   - Add header_rows parameter to __init__
   - Modify read() method to use header_rows if specified
   - Update class docstring

2. astropy/io/ascii/tests/test_rst.py
   - Add tests for header_rows parameter
   - Test both specified and auto-detect modes
   
3. astropy/io/ascii/ui.py (if needed)
   - Update read() function to pass header_rows to RST class
"""

# Example test case:
def test_rst_header_rows():
    """Test RST reader with header_rows parameter"""
    lines = [
        "===== ===== =====",
        "Col1  Col2  Col3",  
        "Unit1 Unit2 Unit3",  # This should be included as header with header_rows=2
        "===== ===== =====",
        "1     2     3",
        "4     5     6",
        "===== ===== ====="
    ]
    
    # With header_rows=2, both Col1/Col2/Col3 and Unit1/Unit2/Unit3 
    # should be treated as header rows