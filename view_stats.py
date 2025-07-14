#!/usr/bin/env python3
"""View and analyze parallel route statistics"""

import os
from collections import defaultdict

def view_statistics(stats_file="parallel_route_stats.txt"):
    """Display statistics from the simple format file"""
    
    if not os.path.exists(stats_file):
        print(f"No statistics file found at: {stats_file}")
        return
    
    stats = []
    with open(stats_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                if len(parts) == 2:
                    stats.append({
                        'task_category': parts[0],
                        'best_model': parts[1]
                    })
    
    if not stats:
        print("No statistics recorded yet.")
        return
    
    print(f"\nParallel Route Statistics Summary")
    print("=" * 80)
    print(f"Total requests: {len(stats)}")
    
    # Task category breakdown
    category_counts = defaultdict(int)
    for row in stats:
        category_counts[row['task_category']] += 1
    
    print("\nTask Categories:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count} ({count/len(stats)*100:.1f}%)")
    
    # Best model breakdown
    best_model_counts = defaultdict(int)
    for row in stats:
        best_model_counts[row['best_model']] += 1
    
    print("\nBest Model Selection:")
    for model, count in sorted(best_model_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model}: {count} ({count/len(stats)*100:.1f}%)")
    
    # Recent entries
    print("\nRecent Entries (last 10):")
    for row in stats[-10:]:
        print(f"  - {row['task_category']} -> {row['best_model']}")
    
    print("\nStatistics saved in:", stats_file)

if __name__ == "__main__":
    view_statistics()