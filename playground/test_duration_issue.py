"""
Test script to demonstrate the DurationField format issue
"""
import datetime

def parse_duration_test():
    """
    Test various duration formats to understand the actual behavior
    """
    test_cases = [
        "14:00",         # 14 minutes (not 14 hours)
        "00:14:00",      # 14 minutes
        "14:00:00",      # 14 hours
        "1:14:00",       # 1 hour 14 minutes
        "1:14:30",       # 1 hour 14 minutes 30 seconds
        "30",            # 30 seconds
        "1:30",          # 1 minute 30 seconds
        "1 14:30:00",    # 1 day 14 hours 30 minutes
    ]
    
    print("Testing duration formats:")
    print("Format pattern should be: [DD] [[HH:]MM:]ss[.uuuuuu]")
    print("Where:")
    print("- [DD] = optional days")
    print("- [[HH:]MM:] = optional hours and minutes (if hours present, minutes required)")
    print("- ss = required seconds")
    print("- [.uuuuuu] = optional microseconds")
    
if __name__ == "__main__":
    parse_duration_test()