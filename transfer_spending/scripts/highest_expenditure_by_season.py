import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the data
df = pd.read_csv('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data/transfer_spending_cleaned.csv')

# Convert expenditure to numeric (remove 'm' and convert to float)
df['Expenditure_numeric'] = df['Expenditure'].str.replace('m', '').astype(float)

# Find the highest expenditure team for each season
highest_per_season = df.loc[df.groupby('Season')['Expenditure_numeric'].idxmax()]

# Sort by season for proper ordering
highest_per_season = highest_per_season.sort_values('Season')

# Define seasons to highlight
highlight_seasons = ['09/10', '17/18', '22/23', '25/26']

# Create colors for bars
colors = ['#FF6B6B' if season in highlight_seasons else 'skyblue' 
          for season in highest_per_season['Season']]
edge_colors = ['#FF0000' if season in highlight_seasons else 'navy' 
               for season in highest_per_season['Season']]
line_widths = [2.5 if season in highlight_seasons else 1.2 
               for season in highest_per_season['Season']]

# Create the bar plot
plt.figure(figsize=(15, 8))
bars = plt.bar(highest_per_season['Season'], highest_per_season['Expenditure_numeric'], 
               color=colors, edgecolor=edge_colors, linewidth=line_widths)

# Customize the plot
plt.title('Highest Transfer Expenditure Team by Season', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Season', fontsize=12, fontweight='bold')
plt.ylabel('Expenditure (€ millions)', fontsize=12, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', alpha=0.3, linestyle='--')

# Add annotations for team name, season, and expenditure
for i, (season, club, expenditure) in enumerate(zip(highest_per_season['Season'], 
                                                   highest_per_season['Club'], 
                                                   highest_per_season['Expenditure_numeric'])):
    # Check if this season should be highlighted
    is_highlighted = season in highlight_seasons
    
    # Position annotation above the bar
    if is_highlighted:
        # Enhanced annotation for highlighted seasons
        plt.annotate(f'★ {club} ★\n{season}\n€{expenditure:.1f}m', 
                    xy=(season, expenditure), 
                    xytext=(0, 15), 
                    textcoords='offset points',
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE4E1', alpha=0.9, 
                             edgecolor='#FF0000', linewidth=2),
                    rotation=0)
    else:
        # Regular annotation for other seasons
        plt.annotate(f'{club}\n{season}\n€{expenditure:.1f}m', 
                    xy=(season, expenditure), 
                    xytext=(0, 10), 
                    textcoords='offset points',
                    ha='center', va='bottom',
                    fontsize=8, 
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'),
                    rotation=0)

# Add legend for highlighted seasons
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#FF6B6B', edgecolor='#FF0000', linewidth=2.5, 
                        label='Highlighted Seasons (09/10, 17/18, 22/23, 25/26)'),
                  Patch(facecolor='skyblue', edgecolor='navy', linewidth=1.2, 
                        label='Other Seasons')]
plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 0.98))

plt.tight_layout()

# Save the plot
plt.savefig('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/highest_expenditure_by_season.png', 
            dpi=300, bbox_inches='tight')

# Display basic statistics
print("Highest expenditure teams by season:")
print(highest_per_season[['Season', 'Club', 'Expenditure', 'League']].to_string(index=False))

print("Plot saved to plots/highest_expenditure_by_season.png")