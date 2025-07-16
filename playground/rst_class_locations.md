# RST Class Implementation Locations in Astropy

## Key Files to Modify

### 1. Main RST Implementation
**File:** `astropy/io/ascii/rst.py`

This file contains:
- `RST` class definition
- `SimpleRSTHeader` class for parsing headers
- `SimpleRSTData` class for parsing data

### 2. Base Classes
**File:** `astropy/io/ascii/fixedwidth.py`

The RST class inherits from `FixedWidth` class, which already has a `header_rows` parameter implementation that can be used as a reference.

### 3. Core Infrastructure
**File:** `astropy/io/ascii/core.py`

Contains:
- `BaseReader` class that all readers inherit from
- `BaseHeader` class for header parsing
- Core parameter handling

### 4. User Interface
**File:** `astropy/io/ascii/ui.py`

The main `read()` function that users call. May need modification to pass the `header_rows` parameter through to the RST reader.

### 5. Tests
**File:** `astropy/io/ascii/tests/test_rst.py`

Add test cases for:
- Single header row with `header_rows=1`
- Multiple header rows with `header_rows=2`
- Auto-detection when `header_rows=None`
- Error handling when `header_rows` exceeds available rows

## Implementation Steps

1. **Modify RST.__init__()** in `rst.py`:
   ```python
   def __init__(self, header_rows=None):
       super().__init__(delimiter_pad=None, bookend=False)
       self.header_rows = header_rows
   ```

2. **Update SimpleRSTHeader** in `rst.py`:
   - Modify the header parsing logic to respect `header_rows` parameter
   - Keep auto-detection as default behavior when `header_rows=None`

3. **Update Documentation**:
   - Add `header_rows` parameter to RST class docstring
   - Update astropy documentation for RST format

4. **Add Tests** in `test_rst.py`:
   - Test various header_rows values
   - Test interaction with existing functionality
   - Test error cases

## Finding the Files

To locate these files in an astropy installation or repository:

```bash
# In astropy source repository
find . -name "rst.py" -path "*/io/ascii/*"
find . -name "fixedwidth.py" -path "*/io/ascii/*"
find . -name "test_rst.py" -path "*/io/ascii/*"

# Or search for class definitions
grep -r "class RST" --include="*.py"
grep -r "class SimpleRSTHeader" --include="*.py"
grep -r "header_rows" --include="*.py" | grep fixedwidth
```

## Current RST Implementation Pattern

The RST class typically follows this pattern:

```python
class RST(FixedWidth):
    """reStructuredText simple table."""
    _format_name = 'rst'
    _description = 'reStructuredText simple table'
    data_class = SimpleRSTData
    header_class = SimpleRSTHeader
    
    def __init__(self):
        super().__init__(delimiter_pad=None, bookend=False)
```

The header parsing is handled by `SimpleRSTHeader`, which identifies header rows as all lines between the first two delimiter lines (lines containing only '=' and spaces).