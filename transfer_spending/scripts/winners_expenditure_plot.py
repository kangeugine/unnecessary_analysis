import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
df = pd.read_csv('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data/transfer_spending_with_winners.csv')

# Filter for winning clubs or Champions League winners
winners_df = df[(df['Club'] == df['Winning Club']) | (df['Club'] == df['Champions League Winners'])].copy()

# Convert expenditure to numeric, removing 'm' suffix
winners_df['Expenditure_numeric'] = winners_df['Expenditure'].str.replace('m', '').astype(float)

# Group by club and keep the row with highest expenditure
winners_max = winners_df.loc[winners_df.groupby('Club')['Expenditure_numeric'].idxmax()]

# Create club labels with season
winners_max['Club_Season'] = winners_max['Club'] + ' ' + winners_max['Season']

# Sort by expenditure in descending order
winners_max = winners_max.sort_values('Expenditure_numeric', ascending=True)

# Define colors for each league
league_colors = {
    'Premier League': '#3498db',
    'LaLiga': '#e74c3c',
    'Serie A': '#2ecc71',
    'Bundesliga': '#f39c12',
    'Ligue 1': '#9b59b6',
    'Saudi Pro League': '#1abc9c',
    'Super League 2017': '#34495e',
    'Eredivisie': '#e67e22',
    'Liga Portugal': '#95a5a6'
}

# Get colors for each club based on league
colors = [league_colors.get(league, '#7f8c8d') for league in winners_max['League']]

# Create horizontal bar plot
plt.figure(figsize=(14, 10))
bars = plt.barh(winners_max['Club_Season'], winners_max['Expenditure_numeric'], color=colors, alpha=0.8)

# Customize plot
plt.xlabel('Transfer Expenditure (millions €)')
plt.title('Highest Transfer Expenditure by Winning Clubs\n(League Winners & Champions League Winners)')
plt.grid(axis='x', alpha=0.3)

# Add value labels on bars
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 5, bar.get_y() + bar.get_height()/2, 
             f'€{width:.0f}m', ha='left', va='center', fontsize=9)

# Create legend
unique_leagues = winners_max['League'].unique()
legend_elements = [plt.Rectangle((0,0),1,1, facecolor=league_colors.get(league, '#7f8c8d'), alpha=0.8) 
                   for league in unique_leagues]
plt.legend(legend_elements, unique_leagues, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/winners_expenditure_plot.png', 
            dpi=300, bbox_inches='tight')
# plt.show()

print(f"Plot saved to: /Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/winners_expenditure_plot.png")
print(f"Total clubs plotted: {len(winners_max)}")