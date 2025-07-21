def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n (int): The position of the Fibonacci number to calculate (0-indexed)
    
    Returns:
        int: The nth Fibonacci number
    
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b