import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the data
df = pd.read_csv('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data/liverpool_spending.csv')

# Convert expenditure to numeric (remove 'm' and convert to float)
df['Expenditure_numeric'] = df['Expenditure'].str.replace('m', '').astype(float)

# Sort by expenditure in descending order (highest on top)
df_sorted = df.sort_values('Expenditure_numeric', ascending=True)

# Create horizontal bar plot
plt.figure(figsize=(10, 6))

# Create red color gradient based on expenditure
normalized_values = df_sorted['Expenditure_numeric'] / df_sorted['Expenditure_numeric'].max()
colors = plt.cm.Reds(normalized_values)

bars = plt.barh(df_sorted['Season'], df_sorted['Expenditure_numeric'], color=colors)

# Customize the plot
plt.xlabel('Expenditure (£m)')
plt.ylabel('Season')
plt.title('Liverpool FC Transfer Expenditure After Winning Major Trophy')
plt.grid(axis='x', alpha=0.3)

# Add value labels on bars
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width + 5, bar.get_y() + bar.get_height()/2, 
             f'£{width:.1f}m', ha='left', va='center')

plt.tight_layout()
plt.savefig('/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/plots/liverpool_horizontal_bar.png', 
            dpi=300, bbox_inches='tight')
print("Plot saved successfully!")