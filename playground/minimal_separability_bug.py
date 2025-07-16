"""
Minimal example to reproduce the separability_matrix bug.

This shows the core issue: when a CompoundModel contains another CompoundModel,
the separability matrix is incorrectly computed as all True (non-separable).
"""

# This would be the minimal code to reproduce the bug:
# (Requires: pip install astropy)

from astropy.modeling import models as m

# Create a compound model with two Linear1D models
cm = m.Linear1D(10) & m.Linear1D(5)
print("Compound model cm:")
print(cm.separability_matrix)
# Output: [[True, False], [False, True]] - CORRECT

# Create the same structure directly
direct = m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)
print("\nDirect compound:")
print(direct.separability_matrix)
# Output: [[True, True, False, False],
#          [True, True, False, False],
#          [False, False, True, False],
#          [False, False, False, True]] - CORRECT

# Create a nested compound model
nested = m.Pix2Sky_TAN() & cm
print("\nNested compound:")
print(nested.separability_matrix)
# Output: [[True, True, True, True],
#          [True, True, True, True],
#          [True, True, True, True],
#          [True, True, True, True]] - INCORRECT!

# The bug: nested compound shows all inputs as non-separable