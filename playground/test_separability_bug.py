#!/usr/bin/env python
"""Test script to reproduce the separability matrix bug with nested CompoundModels."""

from astropy.modeling import models as m
from astropy.modeling.separable import separability_matrix

print("Testing separability matrix for nested CompoundModels")
print("=" * 60)

# Test 1: Simple compound model
cm = m.Linear1D(10) & m.Linear1D(5)
print("\nTest 1: Simple compound model (cm = Linear1D(10) & Linear1D(5))")
matrix1 = separability_matrix(cm)
print("Separability matrix:")
print(matrix1)
print("Expected: diagonal matrix (separable)")

# Test 2: Complex compound model (not nested)
model2 = m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)
print("\nTest 2: Complex compound model (Pix2Sky_TAN() & Linear1D(10) & Linear1D(5))")
matrix2 = separability_matrix(model2)
print("Separability matrix:")
print(matrix2)
print("Expected: block diagonal matrix (separable within blocks)")

# Test 3: Nested compound model (THE BUG)
model3 = m.Pix2Sky_TAN() & cm
print("\nTest 3: Nested compound model (Pix2Sky_TAN() & cm)")
print("where cm = Linear1D(10) & Linear1D(5)")
matrix3 = separability_matrix(model3)
print("Separability matrix:")
print(matrix3)
print("Expected: block diagonal matrix (same as Test 2)")
print("ACTUAL: All True in bottom-right block (BUG!)")

# Verify the bug
print("\n" + "=" * 60)
print("BUG VERIFICATION:")
print("Bottom-right 2x2 block of Test 2 (correct):")
print(matrix2[2:, 2:])
print("\nBottom-right 2x2 block of Test 3 (incorrect due to bug):")
print(matrix3[2:, 2:])
print("\nThese should be identical, but they're not!")