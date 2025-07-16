"""
Demonstration of what's likely happening inside the _cstack and _coord_matrix
functions that causes the nested compound model separability bug.
"""

import numpy as np
from astropy.modeling import models as m


def visualize_separability_computation():
    """Visualize how separability matrices should be computed vs how they are."""
    
    print("=" * 80)
    print("UNDERSTANDING THE SEPARABILITY BUG")
    print("=" * 80)
    
    # Create our models
    pix2sky = m.Pix2Sky_TAN()
    linear1 = m.Linear1D(10)
    linear2 = m.Linear1D(5)
    cm = linear1 & linear2
    
    print("\n1. Individual Model Properties:")
    print(f"   Pix2Sky_TAN: {pix2sky.n_inputs} inputs -> {pix2sky.n_outputs} outputs")
    print(f"   Linear1D(10): {linear1.n_inputs} inputs -> {linear1.n_outputs} outputs")
    print(f"   Linear1D(5): {linear2.n_inputs} inputs -> {linear2.n_outputs} outputs")
    print(f"   cm (Linear1D & Linear1D): {cm.n_inputs} inputs -> {cm.n_outputs} outputs")
    
    print("\n2. Separability Matrices of Individual Components:")
    print(f"   Pix2Sky_TAN separability:\n{pix2sky.separability_matrix}")
    print(f"   cm separability:\n{cm.separability_matrix}")
    
    # Show what should happen
    print("\n3. How _cstack SHOULD combine these matrices:")
    print("   For Pix2Sky_TAN() & cm:")
    print("   - Pix2Sky uses inputs [0,1] and produces outputs [0,1]")
    print("   - cm uses inputs [2,3] and produces outputs [2,3]")
    print("\n   The combined 4x4 matrix should be:")
    
    correct_matrix = np.array([
        [True, True, False, False],   # output 0 depends on inputs 0,1
        [True, True, False, False],   # output 1 depends on inputs 0,1
        [False, False, True, False],  # output 2 depends on input 2
        [False, False, False, True]   # output 3 depends on input 3
    ])
    print(correct_matrix)
    
    # Show what actually happens
    nested = pix2sky & cm
    print("\n4. What ACTUALLY happens:")
    print(f"   Nested model separability:\n{nested.separability_matrix}")
    
    print("\n5. The BUG Analysis:")
    print("   The bug occurs because _cstack likely does something like this:")
    print("   - It sees that 'cm' already has a separability matrix")
    print("   - Instead of properly positioning it in the larger matrix,")
    print("     it falls back to 'all True' (conservative non-separable)")
    
    # Demonstrate the pattern
    print("\n6. Pseudo-code of what's likely happening:")
    print("""
    def _cstack(left, right):
        if has_separability_matrix(right):
            # BUG: Doesn't know how to position pre-computed matrix
            # Falls back to conservative all-True
            return np.ones((n_inputs_total, n_outputs_total), dtype=bool)
        else:
            # Works correctly for simple models
            return compute_fresh_separability()
    """)
    
    print("\n7. The coordinate mapping issue:")
    print("   When _coord_matrix builds coordinate mappings:")
    print("   - For simple models: maps inputs directly to outputs")
    print("   - For nested models: loses track of proper index offsets")
    print("   - Result: assumes all inputs affect all outputs")


def demonstrate_block_positioning():
    """Show how the matrices should be positioned in block form."""
    
    print("\n" + "=" * 80)
    print("BLOCK MATRIX POSITIONING")
    print("=" * 80)
    
    print("\nFor A & B where A is 2x2 and B is 2x2:")
    print("The result should be a 4x4 block diagonal matrix:\n")
    
    # Create visual representation
    print("     Input indices:  0  1  2  3")
    print("                    -----------")
    print("Output index 0:    | A  A  .  . |")
    print("Output index 1:    | A  A  .  . |")
    print("Output index 2:    | .  .  B  B |")
    print("Output index 3:    | .  .  B  B |")
    print("                    -----------")
    
    print("\nWhere:")
    print("  A = True (from Pix2Sky_TAN separability)")
    print("  B = True/False (from cm's diagonal separability)")
    print("  . = False (no connection)")
    
    print("\nBut the bug produces:")
    print("     Input indices:  0  1  2  3")
    print("                    -----------")
    print("Output index 0:    | T  T  T  T |")
    print("Output index 1:    | T  T  T  T |")
    print("Output index 2:    | T  T  T  T |")
    print("Output index 3:    | T  T  T  T |")
    print("                    -----------")
    
    print("\nAll True = assumes everything depends on everything!")


def show_index_offset_problem():
    """Demonstrate the index offset issue."""
    
    print("\n" + "=" * 80)
    print("INDEX OFFSET PROBLEM")
    print("=" * 80)
    
    print("\nWhen combining Pix2Sky_TAN() & (Linear1D & Linear1D):")
    print("\n1. Pix2Sky_TAN contribution:")
    print("   - Takes inputs at indices [0, 1]")
    print("   - Produces outputs at indices [0, 1]")
    
    print("\n2. The compound model (Linear1D & Linear1D) contribution:")
    print("   - Takes inputs at indices [2, 3] (OFFSET BY 2)")
    print("   - Produces outputs at indices [2, 3] (OFFSET BY 2)")
    print("   - Has internal separability: [[True, False], [False, True]]")
    
    print("\n3. The bug likely occurs because:")
    print("   - The pre-computed 2x2 matrix for (Linear1D & Linear1D)")
    print("   - Needs to be placed at position [2:4, 2:4] in the 4x4 matrix")
    print("   - But the offset calculation fails for nested models")
    
    print("\n4. Correct index mapping:")
    print("   Input 0 -> Output 0,1 (Pix2Sky)")
    print("   Input 1 -> Output 0,1 (Pix2Sky)")
    print("   Input 2 -> Output 2 only (Linear1D #1)")
    print("   Input 3 -> Output 3 only (Linear1D #2)")
    
    print("\n5. Buggy behavior suggests:")
    print("   All inputs -> All outputs (complete loss of structure)")


if __name__ == "__main__":
    visualize_separability_computation()
    demonstrate_block_positioning()
    show_index_offset_problem()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nThe bug occurs because the _cstack function doesn't properly handle")
    print("pre-computed separability matrices from nested compound models.")
    print("It needs to:")
    print("1. Calculate proper index offsets")
    print("2. Place the nested matrix at the correct position")
    print("3. Preserve the internal structure of nested models")
    print("\nInstead, it falls back to a conservative 'all True' matrix.")