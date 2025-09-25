#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Set matplotlib to use non-interactive backend
plt.switch_backend('Agg')

def create_top10_expenditure_plot():
    """Create a plot showing the top 10 expenditure for club and season"""
    
    # Read the cleaned CSV file
    df = pd.read_csv('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data/transfer_spending_cleaned.csv')
    
    # Convert Expenditure to numeric, removing 'm' suffix and handling any non-numeric values
    df['Expenditure'] = df['Expenditure'].astype(str).str.replace('m', '').str.replace('€', '').str.replace(',', '')
    df['Expenditure'] = pd.to_numeric(df['Expenditure'], errors='coerce')
    df['Expenditure'] = df['Expenditure'].fillna(0)
    
    # Filter out rows with missing data
    df_clean = df[(df['Expenditure'] > 0) & (df['Club'].notna()) & (df['Season'].notna()) & (df['Season'] != '')]
    
    # Get top 10 expenditures (reverse order so highest is on top)
    top10 = df_clean.nlargest(10, 'Expenditure').iloc[::-1]
    
    # Create club-season labels
    top10['Club_Season'] = top10['Club'] + '\n' + top10['Season']
    
    # Define colors for different leagues
    league_colors = {
        'Premier League': '#38003c',      # Purple
        'LaLiga': '#FF6B35',              # Orange-red
        'Serie A': '#0066CC',             # Blue
        'Bundesliga': '#D20515',          # Red
        'Ligue 1': '#1f4788',             # Dark blue
        'Saudi Pro League': '#006C35',    # Green
        'Others': '#808080'               # Gray
    }
    
    # Map colors to bars based on club (Liverpool gets red, others by league)
    bar_colors = []
    for _, row in top10.iterrows():
        if 'Liverpool' in row['Club']:
            bar_colors.append('#FF0000')  # Red for Liverpool
        else:
            bar_colors.append(league_colors.get(row['League'], league_colors['Others']))
    
    # Create the plot
    plt.figure(figsize=(16, 10))
    
    # Create horizontal bar chart
    bars = plt.barh(range(len(top10)), top10['Expenditure'], color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, top10['Expenditure'])):
        width = bar.get_width()
        plt.text(width + width * 0.01, bar.get_y() + bar.get_height()/2.,
                f'€{value:,.1f}M', ha='left', va='center', fontweight='bold', fontsize=10)
    
    # Customize the plot
    plt.title('Top 10 Transfer Expenditures by Club and Season\n(Transfer Spending Data)', 
              fontsize=18, fontweight='bold', pad=20)
    plt.ylabel('Club and Season', fontsize=14, fontweight='bold')
    plt.xlabel('Expenditure (Millions €)', fontsize=14, fontweight='bold')
    
    # Set y-axis labels (no rotation needed for horizontal bars)
    plt.yticks(range(len(top10)), top10['Club_Season'], fontsize=11)
    plt.xticks(fontsize=11)
    plt.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Create legend for leagues (add Liverpool as special case)
    unique_leagues = top10['League'].unique()
    legend_handles = []
    legend_labels = []
    
    # Add Liverpool first if it's in the data
    if any('Liverpool' in club for club in top10['Club']):
        legend_handles.append(plt.Rectangle((0,0),1,1, color='#FF0000', alpha=0.8))
        legend_labels.append('Liverpool FC')
    
    for league in unique_leagues:
        color = league_colors.get(league, league_colors['Others'])
        legend_handles.append(plt.Rectangle((0,0),1,1, color=color, alpha=0.8))
        legend_labels.append(league)
    
    plt.legend(legend_handles, legend_labels, loc='lower right', fontsize=11, framealpha=0.9)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    output_path = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/top10_expenditure.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    print(f"\nTop 10 expenditure plot saved to: {output_path}")
    
    # Print statistics
    print("\nTop 10 Transfer Expenditures:")
    print("-" * 80)
    print(f"{'Rank':<6} {'Club':<25} {'Season':<10} {'League':<18} {'Expenditure':<12}")
    print("-" * 80)
    
    for i, (_, row) in enumerate(top10.iterrows(), 1):
        print(f"{i:<6} {row['Club']:<25} {row['Season']:<10} {row['League']:<18} €{row['Expenditure']:,.1f}M")
    
    print("-" * 80)
    
    # Additional statistics
    print(f"\nTotal expenditure (Top 10): €{top10['Expenditure'].sum():,.1f}M")
    print(f"Average expenditure (Top 10): €{top10['Expenditure'].mean():,.1f}M")
    print(f"Highest expenditure: {top10.iloc[0]['Club']} ({top10.iloc[0]['Season']}) - €{top10.iloc[0]['Expenditure']:,.1f}M")
    
    # League breakdown
    print("\nLeague breakdown (Top 10):")
    league_counts = top10['League'].value_counts()
    for league, count in league_counts.items():
        league_total = top10[top10['League'] == league]['Expenditure'].sum()
        print(f"  {league}: {count} clubs, €{league_total:,.1f}M total")
    
    return top10

if __name__ == "__main__":
    create_top10_expenditure_plot()