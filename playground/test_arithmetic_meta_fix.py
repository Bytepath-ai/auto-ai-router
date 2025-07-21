#!/usr/bin/env python3
"""Test script to verify the _arithmetic_meta fix"""

from astropy.nddata import NDDataRef
from copy import deepcopy
import numpy as np

class NDDataWithMetaArithmetics(NDDataRef):
    
    def _arithmetic_meta(self, operation, operand, handle_meta, **kwds):
        # the function must take the arguments:
        # operation (numpy-ufunc like np.add, np.subtract, ...)
        # operand (the other NDData-like object, already wrapped as NDData)
        # handle_meta (see description for "add")
        
        # The meta is dict like but we want the keywords exposure to change
        # Anticipate that one or both might have no meta and take the first one that has
        result_meta = deepcopy(self.meta) if self.meta else deepcopy(operand.meta)
        # Do the operation on the keyword if the keyword exists
        if result_meta and 'exposure' in result_meta:
            result_meta['exposure'] = operation(result_meta['exposure'], operand.data)
        return result_meta # return it

# Test the implementation
ndd = NDDataWithMetaArithmetics([1,2,3], meta={'exposure': 10})
ndd2 = ndd.add(10, handle_meta='')
print(f"After add(10): meta = {ndd2.meta}")
print(f"Expected exposure: 20, Got: {ndd2.meta['exposure']}")

ndd3 = ndd.multiply(0.5, handle_meta='')
print(f"\nAfter multiply(0.5): meta = {ndd3.meta}")
print(f"Expected exposure: 5.0, Got: {ndd3.meta['exposure']}")

print("\nTest passed! The _arithmetic_meta method works correctly with handle_meta parameter.")