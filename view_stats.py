#!/usr/bin/env python3
"""View and analyze parallel route statistics"""

import os
import sqlite3
from collections import defaultdict
from datetime import datetime

def view_statistics(stats_db="parallel_route_stats.db"):
    """Display statistics from the SQLite database"""
    
    if not os.path.exists(stats_db):
        print(f"No statistics database found at: {stats_db}")
        return
    
    conn = sqlite3.connect(stats_db)
    cursor = conn.cursor()
    
    # Get all statistics
    cursor.execute('''
        SELECT timestamp, task_name, task_category, best_model,
               claude_code_score, claude_opus_score, o3_score,
               gpt4o_score, gpt4o_mini_score, grok4_score, gemini_25_pro_score
        FROM route_statistics
        ORDER BY timestamp DESC
    ''')
    
    stats = []
    for row in cursor.fetchall():
        stats.append({
            'timestamp': row[0],
            'task_name': row[1],
            'task_category': row[2],
            'best_model': row[3],
            'scores': {
                'Claude Code': row[4] or 0,
                'Claude Opus 4': row[5] or 0,
                'O3': row[6] or 0,
                'GPT-4o': row[7] or 0,
                'GPT-4o-mini': row[8] or 0,
                'Grok-4': row[9] or 0,
                'Gemini 2.5 Pro': row[10] or 0
            }
        })
    
    if not stats:
        print("No statistics recorded yet.")
        conn.close()
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
    
    # Model performance by average score
    model_avg_scores = defaultdict(list)
    for row in stats:
        for model, score in row['scores'].items():
            if score > 0:
                model_avg_scores[model].append(score)
    
    print("\nAverage Model Scores:")
    avg_scores = {}
    for model, scores in model_avg_scores.items():
        avg = sum(scores) / len(scores) if scores else 0
        avg_scores[model] = avg
    
    for model, avg in sorted(avg_scores.items(), key=lambda x: x[1], reverse=True):
        if avg > 0:
            print(f"  {model}: {avg:.1f}/10")
    
    # Recent entries
    print("\nRecent Entries (last 10):")
    for row in stats[:10]:  # Already sorted by timestamp DESC
        timestamp = datetime.fromisoformat(row['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"  - [{timestamp}] {row['task_name']} ({row['task_category']}) -> {row['best_model']}")
    
    print("\nStatistics saved in:", stats_db)
    conn.close()

if __name__ == "__main__":
    import sys
    view_statistics()