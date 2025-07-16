# Complete implementation guide for adding header_rows to RST class

"""
IMPLEMENTATION GUIDE: Adding header_rows parameter to astropy.io.ascii.RST
"""

# 1. CURRENT RST IMPLEMENTATION (typical structure in astropy/io/ascii/rst.py)

class RST(FixedWidth):
    """reStructuredText simple table.
    
    See: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#simple-tables
    
    Example::
    
        ==== ===== ======
        Col1  Col2  Col3
        ==== ===== ======
          1    2.3  Hello
          2    4.5  World
        ==== ===== ======
    
    Currently supports only single-line column names.
    """
    
    _format_name = 'rst'
    _description = 'reStructuredText simple table'
    data_class = SimpleRSTData
    header_class = SimpleRSTHeader
    
    def __init__(self):
        super().__init__(delimiter_pad=None, bookend=False)

# 2. MODIFIED RST IMPLEMENTATION WITH header_rows

class RST(FixedWidth):
    """reStructuredText simple table.
    
    See: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#simple-tables
    
    Example::
    
        ==== ===== ======
        Col1  Col2  Col3
        ==== ===== ======
          1    2.3  Hello
          2    4.5  World
        ==== ===== ======
    
    Parameters
    ----------
    header_rows : int, optional
        Number of header rows to read. Default is None, which auto-detects
        header rows between the first and second delimiter lines.
    """
    
    _format_name = 'rst'
    _description = 'reStructuredText simple table'
    data_class = SimpleRSTData
    header_class = SimpleRSTHeader
    
    def __init__(self, header_rows=None):
        super().__init__(delimiter_pad=None, bookend=False)
        self.header_rows = header_rows

# 3. MODIFIED SimpleRSTHeader CLASS

class SimpleRSTHeader(FixedWidthHeader):
    """Header reader for RST tables with header_rows support"""
    
    def get_lines(self, lines):
        """Get header lines from RST table"""
        # Find delimiter lines (lines with only '=' and spaces)
        delim_indices = []
        for i, line in enumerate(lines):
            clean_line = line.strip()
            if clean_line and set(clean_line) <= {'=', ' '}:
                delim_indices.append(i)
        
        if len(delim_indices) < 2:
            raise ValueError('RST table must have at least two delimiter lines')
        
        # Get header lines between first two delimiters
        header_start = delim_indices[0] + 1
        header_end = delim_indices[1]
        
        if self.header_rows is not None:
            # Use specified number of header rows
            header_lines = lines[header_start:header_start + self.header_rows]
            if len(header_lines) < self.header_rows:
                raise ValueError(f'Table has only {len(header_lines)} header lines, '
                                 f'but header_rows={self.header_rows} was specified')
        else:
            # Auto-detect: all lines between delimiters
            header_lines = lines[header_start:header_end]
        
        return header_lines

# 4. USAGE EXAMPLES

# Example 1: Single header row (default behavior)
rst_table1 = """
==== ===== ======
Col1  Col2  Col3
==== ===== ======
  1    2.3  Hello
  2    4.5  World
==== ===== ======
"""

# Example 2: Multiple header rows
rst_table2 = """
==== ===== ======
Col1  Col2  Col3
m     km    desc
==== ===== ======
  1    2.3  Hello
  2    4.5  World
==== ===== ======
"""

# Reading with header_rows:
from astropy.io import ascii

# Auto-detect (reads both header lines)
table1 = ascii.read(rst_table2, format='rst')

# Specify single header row (only reads "Col1 Col2 Col3")
table2 = ascii.read(rst_table2, format='rst', header_rows=1)

# Specify two header rows (reads both lines as headers)
table3 = ascii.read(rst_table2, format='rst', header_rows=2)

# 5. TEST CASES TO ADD

def test_rst_header_rows_single():
    """Test RST reader with header_rows=1"""
    text = """
    ==== ===== ======
    Col1  Col2  Col3
    m     km    desc
    ==== ===== ======
      1    2.3  Hello
      2    4.5  World
    ==== ===== ======
    """
    # With header_rows=1, only first line is header
    t = ascii.read(text, format='rst', header_rows=1)
    assert list(t.colnames) == ['Col1', 'Col2', 'Col3']
    assert len(t) == 3  # Includes the units row as data

def test_rst_header_rows_multiple():
    """Test RST reader with header_rows=2"""
    text = """
    ==== ===== ======
    Col1  Col2  Col3
    m     km    desc
    ==== ===== ======
      1    2.3  Hello
      2    4.5  World
    ==== ===== ======
    """
    # With header_rows=2, both lines are headers
    t = ascii.read(text, format='rst', header_rows=2)
    assert list(t.colnames) == ['Col1', 'Col2', 'Col3']
    assert list(t['Col1'].unit) == 'm'
    assert list(t['Col2'].unit) == 'km'
    assert len(t) == 2  # Only data rows

def test_rst_header_rows_too_many():
    """Test RST reader with header_rows exceeding available lines"""
    text = """
    ==== ===== ======
    Col1  Col2  Col3
    ==== ===== ======
      1    2.3  Hello
    ==== ===== ======
    """
    with pytest.raises(ValueError, match='Table has only 1 header lines'):
        ascii.read(text, format='rst', header_rows=2)

# 6. INTEGRATION POINTS

# In astropy/io/ascii/ui.py, the read() function should pass header_rows:
def read(table, format=None, header_rows=None, **kwargs):
    """Read table with format auto-detection"""
    if format == 'rst':
        reader = RST(header_rows=header_rows)
        # ... rest of implementation

# 7. DOCUMENTATION TO UPDATE

"""
In docs/io/ascii/index.rst or similar:

RST Format
----------

The ``rst`` format reads reStructuredText simple tables. 

Parameters
~~~~~~~~~~

header_rows : int, optional
    Number of rows between the first two delimiter lines to treat as 
    header rows. If not specified, all rows between delimiters are 
    treated as headers.

Examples
~~~~~~~~

Reading with multiple header rows::

    >>> from astropy.io import ascii
    >>> table = '''
    ... ==== ===== ======
    ... Col1  Col2  Col3
    ... m     km    desc
    ... ==== ===== ======
    ...   1    2.3  Hello
    ...   2    4.5  World
    ... ==== ===== ======
    ... '''
    >>> # Read only first row as header
    >>> t1 = ascii.read(table, format='rst', header_rows=1)
    >>> # Read both rows as headers (with units)
    >>> t2 = ascii.read(table, format='rst', header_rows=2)
"""