"""
Test file to reproduce the separability_matrix bug with nested CompoundModels.

This test demonstrates the issue where:
1. cm = m.Linear1D(10) & m.Linear1D(5) has correct diagonal separability
2. m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5) has correct separability
3. m.Pix2Sky_TAN() & cm incorrectly shows the linear models as non-separable

Bug report: https://github.com/astropy/astropy/issues/16722

Requirements:
    pip install astropy numpy

To run this test:
    python test_separability_bug.py

Expected behavior:
    All three cases should produce the same separability matrix pattern where:
    - Pix2Sky_TAN inputs (0,1) are separable from Linear1D inputs (2,3)
    - Linear1D(10) input (2) is separable from Linear1D(5) input (3)

Actual behavior (bug):
    Case 3 incorrectly shows all inputs as non-separable (all True in matrix)
"""

import numpy as np
from astropy.modeling import models as m


def print_separability_info(model, description):
    """Helper function to print model and its separability matrix."""
    print(f"\n{description}")
    print(f"Model: {model}")
    print(f"Separability matrix:\n{model.separability_matrix}")
    print(f"Is separable: {model.separable}")
    

def test_separability_bug():
    """Test the three cases mentioned in the bug report."""
    
    print("=" * 70)
    print("Testing separability_matrix bug with nested CompoundModels")
    print("=" * 70)
    
    # Case 1: Direct compound of two Linear1D models
    # This should have correct diagonal separability
    cm = m.Linear1D(10) & m.Linear1D(5)
    print_separability_info(cm, "Case 1: m.Linear1D(10) & m.Linear1D(5)")
    
    # Expected: diagonal matrix [[True, False], [False, True]]
    expected_1 = np.array([[True, False], [False, True]])
    print(f"Expected separability matrix:\n{expected_1}")
    print(f"Matches expected: {np.array_equal(cm.separability_matrix, expected_1)}")
    
    # Case 2: Direct compound of all three models
    # This should have correct separability
    model_direct = m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)
    print_separability_info(model_direct, "\nCase 2: m.Pix2Sky_TAN() & m.Linear1D(10) & m.Linear1D(5)")
    
    # Expected: 4x4 matrix with appropriate separability
    expected_2 = np.array([
        [True, True, False, False],
        [True, True, False, False],
        [False, False, True, False],
        [False, False, False, True]
    ])
    print(f"Expected separability matrix:\n{expected_2}")
    print(f"Matches expected: {np.array_equal(model_direct.separability_matrix, expected_2)}")
    
    # Case 3: Compound model with nested compound model
    # This incorrectly shows the linear models as non-separable
    model_nested = m.Pix2Sky_TAN() & cm
    print_separability_info(model_nested, "\nCase 3: m.Pix2Sky_TAN() & cm (where cm = m.Linear1D(10) & m.Linear1D(5))")
    
    # Expected: Should be the same as Case 2
    print(f"Expected separability matrix:\n{expected_2}")
    print(f"Matches expected: {np.array_equal(model_nested.separability_matrix, expected_2)}")
    
    # Demonstrate the bug
    print("\n" + "=" * 70)
    print("BUG DEMONSTRATION:")
    print("=" * 70)
    
    if not np.array_equal(model_direct.separability_matrix, model_nested.separability_matrix):
        print("❌ BUG CONFIRMED: The separability matrices are different!")
        print("\nDirect compound (Case 2) separability matrix:")
        print(model_direct.separability_matrix)
        print("\nNested compound (Case 3) separability matrix:")
        print(model_nested.separability_matrix)
        
        # Show the specific issue
        print("\nThe issue is that in Case 3, the linear models are incorrectly")
        print("shown as non-separable (all True values in the matrix).")
    else:
        print("✓ No bug found: The separability matrices are the same.")
    
    # Additional analysis
    print("\n" + "=" * 70)
    print("ADDITIONAL ANALYSIS:")
    print("=" * 70)
    
    # Check individual model properties
    print("\nIndividual model properties:")
    print(f"Pix2Sky_TAN n_inputs: {m.Pix2Sky_TAN().n_inputs}, n_outputs: {m.Pix2Sky_TAN().n_outputs}")
    print(f"Linear1D(10) n_inputs: {m.Linear1D(10).n_inputs}, n_outputs: {m.Linear1D(10).n_outputs}")
    print(f"Linear1D(5) n_inputs: {m.Linear1D(5).n_inputs}, n_outputs: {m.Linear1D(5).n_outputs}")
    
    print(f"\nCompound model (cm) properties:")
    print(f"cm n_inputs: {cm.n_inputs}, n_outputs: {cm.n_outputs}")
    
    print(f"\nFull model properties:")
    print(f"model_direct n_inputs: {model_direct.n_inputs}, n_outputs: {model_direct.n_outputs}")
    print(f"model_nested n_inputs: {model_nested.n_inputs}, n_outputs: {model_nested.n_outputs}")


if __name__ == "__main__":
    test_separability_bug()