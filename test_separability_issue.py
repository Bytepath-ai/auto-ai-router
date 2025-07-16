from astropy.modeling import models as m
from astropy.modeling.separable import separability_matrix

# Test case 1: Simple compound model
cm = m.Linear1D(10) & m.Linear1D(5)
print("Test 1 - Simple compound model (Linear1D & Linear1D):")
print(separability_matrix(cm))
print()

# Test case 2: More complex model
model2 = m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)
print("Test 2 - Complex model (Pix2Sky_TAN & Linear1D & Linear1D):")
print(separability_matrix(model2))
print()

# Test case 3: Nested compound model (the problematic case)
model3 = m.Pix2Sky_TAN() & cm
print("Test 3 - Nested compound model (Pix2Sky_TAN & (Linear1D & Linear1D)):")
print(separability_matrix(model3))
print()

# Expected result for Test 3 should be the same as Test 2
print("Expected result for Test 3 (should match Test 2):")
print(separability_matrix(model2))