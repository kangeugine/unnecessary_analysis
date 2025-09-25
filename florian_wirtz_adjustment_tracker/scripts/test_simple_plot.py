"""
Simple test to debug the scatter plot visualization
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def test_simple_plot():
    # Load data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'wirtz_performance_data.csv')
    df = pd.read_csv(data_path)

    print("Data loaded:")
    print(df)

    # Create a simple plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Separate data
    baseline_data = df[df['opponent'].isin(['2023-2024', '2024-2025'])].copy()
    match_data = df[~df['opponent'].isin(['2023-2024', '2024-2025'])].copy()

    print(f"\nBaseline data ({len(baseline_data)} points):")
    print(baseline_data[['opponent', 'CII', 'GTI']])

    print(f"\nMatch data ({len(match_data)} points):")
    print(match_data[['opponent', 'CII', 'GTI']])

    # Plot baseline points
    ax.scatter(baseline_data['CII'], baseline_data['GTI'],
               c='green', s=200, alpha=0.9, edgecolors='white', linewidth=2, label='Baseline')

    # Plot match points
    ax.scatter(match_data['CII'], match_data['GTI'],
               c='red', s=200, alpha=0.9, edgecolors='white', linewidth=2, label='Matches')

    # Add labels for all points
    for _, row in df.iterrows():
        ax.annotate(row['opponent'],
                   (row['CII'], row['GTI']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=10, color='white')

    # Style
    ax.set_xlabel('Creative Impact Index (CII)', color='white')
    ax.set_ylabel('Goal Threat Index (GTI)', color='white')
    ax.set_title('Wirtz Performance Test Plot', color='white')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Set axis limits with some padding
    x_min, x_max = df['CII'].min() * 0.9, df['CII'].max() * 1.1
    y_min, y_max = df['GTI'].min() * 0.9, df['GTI'].max() * 1.1
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    print(f"\nAxis limits: X=({x_min:.3f}, {x_max:.3f}), Y=({y_min:.3f}, {y_max:.3f})")

    # Save
    output_path = os.path.join(script_dir, '..', 'plots', 'test_simple_plot.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor='#0E1117', dpi=150, bbox_inches='tight')
    print(f"\nTest plot saved to: {output_path}")

    plt.show()

if __name__ == "__main__":
    test_simple_plot()