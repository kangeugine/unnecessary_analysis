#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set matplotlib to use non-interactive backend
plt.switch_backend('Agg')

def create_ranking_based_histogram():
    """Create a histogram showing expenditure by season with ranking bins (top 10, top 25, top 50, top 100, top 200)"""
    
    # Read the cleaned CSV file
    df = pd.read_csv('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data/transfer_spending_cleaned.csv')
    
    # Convert Expenditure to numeric, removing 'm' suffix and handling any non-numeric values
    df['Expenditure'] = df['Expenditure'].astype(str).str.replace('m', '').str.replace('€', '').str.replace(',', '')
    df['Expenditure'] = pd.to_numeric(df['Expenditure'], errors='coerce')
    df['Expenditure'] = df['Expenditure'].fillna(0)
    
    # Filter out rows with missing ranks, expenditure, or seasons
    df_clean = df[(df['Rank'].notna()) & (df['Expenditure'] > 0) & (df['Season'].notna()) & (df['Season'] != '')]
    
    # Define ranking bins
    ranking_bins = [
        (1, 10, 'Top 10'),
        (11, 25, 'Top 11-25'),
        (26, 50, 'Top 26-50'),
        (51, 100, 'Top 51-100'),
        (101, 200, 'Top 101-200')
    ]
    
    # Get unique seasons and sort them
    seasons = sorted(df_clean['Season'].unique(), key=lambda x: x.split('/')[0] if '/' in str(x) else '00')
    
    # Define colors for each ranking bin
    colors = ['#FF6B35', '#38003c', '#0066CC', '#D20515', '#1f4788']
    
    # Create data structure for stacked bar chart
    bin_data = {}
    bin_labels = []
    
    for i, (start_rank, end_rank, label) in enumerate(ranking_bins):
        bin_labels.append(label)
        bin_data[label] = []
        
        for season in seasons:
            # Filter data for this season and ranking bin
            season_bin_df = df_clean[
                (df_clean['Season'] == season) & 
                (df_clean['Rank'] >= start_rank) & 
                (df_clean['Rank'] <= end_rank)
            ]
            total_expenditure = season_bin_df['Expenditure'].sum()
            bin_data[label].append(total_expenditure)
    
    # Create the stacked bar chart
    plt.figure(figsize=(16, 10))
    
    # Create stacked bars
    bottom = np.zeros(len(seasons))
    bars = []
    
    for i, label in enumerate(bin_labels):
        bars.append(plt.bar(seasons, bin_data[label], bottom=bottom, 
                           color=colors[i], label=label, alpha=0.8, 
                           edgecolor='white', linewidth=0.5))
        bottom += np.array(bin_data[label])
    
    # Add total expenditure labels on top of bars
    for i, season in enumerate(seasons):
        total = sum(bin_data[label][i] for label in bin_labels)
        if total > 0:
            plt.text(i, total + total * 0.01, f'€{total:,.0f}M', 
                    ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Customize the plot
    plt.title('Transfer Expenditure by Season and Ranking Bins\n(Transfer Spending Data)', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Season', fontsize=14, fontweight='bold')
    plt.ylabel('Total Expenditure (Millions)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(fontsize=11)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add legend inside the plot (upper left)
    plt.legend(loc='upper left', fontsize=11, framealpha=0.9)
    
    # Add annotation for Real Madrid in 09/10 season
    season_idx = seasons.index('09/10')
    # Find the y-position for the Top 11-25 bin in 09/10 season (top of the bin)
    y_position = bin_data['Top 10'][season_idx] + bin_data['Top 11-25'][season_idx]
    
    # Add arrow annotation (pointing down from above)
    plt.annotate('Real Madrid\n09/10 Season\n(Rank 17)\n€258.5M', 
                xy=(season_idx, y_position), 
                xytext=(season_idx, y_position + 800),
                arrowprops=dict(arrowstyle='->', color='red', lw=3),
                fontsize=14, fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='yellow', alpha=0.9),
                ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/ranking_based_histogram.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    print(f"\nRanking-based histogram saved to: {output_path}")
    
    # Print statistics by season
    print("\nExpenditure Analysis by Season and Ranking Bins:")
    print("-" * 100)
    print(f"{'Season':<10} {'Top 10':<10} {'Top 11-25':<10} {'Top 26-50':<10} {'Top 51-100':<11} {'Top 101-200':<11} {'Total':<10}")
    print("-" * 100)
    
    for i, season in enumerate(seasons):
        row = f"{season:<10} "
        total_season = 0
        for label in bin_labels:
            value = bin_data[label][i]
            row += f"€{value:<9,.0f} "
            total_season += value
        row += f"€{total_season:<9,.0f}"
        print(row)
    
    print("-" * 100)
    
    # Print totals by ranking bin
    print("\nTotal Expenditure by Ranking Bin (all seasons):")
    print("-" * 50)
    for label in bin_labels:
        total = sum(bin_data[label])
        print(f"{label}: €{total:,.0f}M")
    
    return bin_data, seasons

if __name__ == "__main__":
    create_ranking_based_histogram()