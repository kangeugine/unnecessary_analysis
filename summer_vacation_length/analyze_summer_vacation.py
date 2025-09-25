import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib style for black background
plt.style.use('dark_background')

# Read the data
df = pd.read_csv('summer_vacation_length/school_data.csv')

# Clean the data - remove rows with missing or <40 days summer vacation
df_clean = df.dropna(subset=['summer_vacation_length_in_days'])
df_clean = df_clean[df_clean['summer_vacation_length_in_days'] >= 40]

print(f"Original data: {len(df)} rows")
print(f"Cleaned data: {len(df_clean)} rows")

# Calculate statistics
avg_vacation = df_clean['summer_vacation_length_in_days'].mean()
median_vacation = df_clean['summer_vacation_length_in_days'].median()

print(f"Average summer vacation length: {avg_vacation:.1f} days")
print(f"Median summer vacation length: {median_vacation:.1f} days")

# 1. Histogram for summer vacation length
plt.figure(figsize=(12, 8))
plt.hist(df_clean['summer_vacation_length_in_days'], bins=15, color='skyblue', alpha=0.7, edgecolor='white')
plt.axvline(avg_vacation, color='red', linestyle='--', linewidth=2, label=f'Average: {avg_vacation:.1f} days')
plt.axvline(median_vacation, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_vacation:.1f} days')
plt.xlabel('Summer Vacation Length (days)', fontsize=12, color='white')
plt.ylabel('Number of Schools', fontsize=12, color='white')
plt.title('Distribution of Summer Vacation Length', fontsize=14, color='white')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('summer_vacation_histogram.png', dpi=300, bbox_inches='tight', facecolor='black')
# plt.show()

# 2. Compare by city (bar plot since we don't have lat/lon for map)
city_stats = df_clean.groupby('city')['summer_vacation_length_in_days'].agg(['mean', 'median', 'count']).round(1)
city_stats = city_stats.sort_values('mean', ascending=False)

plt.figure(figsize=(14, 8))
x = np.arange(len(city_stats))
width = 0.35

plt.bar(x - width/2, city_stats['mean'], width, label='Average', color='lightcoral', alpha=0.8)
plt.bar(x + width/2, city_stats['median'], width, label='Median', color='lightgreen', alpha=0.8)

plt.xlabel('City', fontsize=12, color='white')
plt.ylabel('Summer Vacation Length (days)', fontsize=12, color='white')
plt.title('Average and Median Summer Vacation Length by City', fontsize=14, color='white')
plt.xticks(x, city_stats.index, rotation=45, ha='right', color='white')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('vacation_by_city.png', dpi=300, bbox_inches='tight', facecolor='black')
# plt.show()

# 3. Compare by public vs private
public_private_stats = df_clean.groupby('public_or_private')['summer_vacation_length_in_days'].agg(['mean', 'median', 'count']).round(1)

plt.figure(figsize=(10, 6))
x = np.arange(len(public_private_stats))
width = 0.35

plt.bar(x - width/2, public_private_stats['mean'], width, label='Average', color='gold', alpha=0.8)
plt.bar(x + width/2, public_private_stats['median'], width, label='Median', color='violet', alpha=0.8)

plt.xlabel('School Type', fontsize=12, color='white')
plt.ylabel('Summer Vacation Length (days)', fontsize=12, color='white')
plt.title('Average and Median Summer Vacation Length by School Type', fontsize=14, color='white')
plt.xticks(x, public_private_stats.index, color='white')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('vacation_by_school_type.png', dpi=300, bbox_inches='tight', facecolor='black')
# plt.show()

# 4. Top 10 schools with longest summer vacation
top_10 = df_clean.nlargest(10, 'summer_vacation_length_in_days')[['school_name', 'city', 'public_or_private', 'summer_vacation_length_in_days']]

plt.figure(figsize=(14, 8))
colors = ['gold' if school_type == 'private' else 'lightblue' for school_type in top_10['public_or_private']]
bars = plt.barh(range(len(top_10)), top_10['summer_vacation_length_in_days'], color=colors, alpha=0.8)

# Add value labels on bars
for i, (bar, days) in enumerate(zip(bars, top_10['summer_vacation_length_in_days'])):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{days:.0f} days', va='center', color='white', fontweight='bold')

plt.yticks(range(len(top_10)), 
           [f"{name}\n({city}, {type_})" for name, city, type_ in 
            zip(top_10['school_name'], top_10['city'], top_10['public_or_private'])],
           fontsize=10, color='white')
plt.xlabel('Summer Vacation Length (days)', fontsize=12, color='white')
plt.title('Top 10 Schools with Longest Summer Vacation', fontsize=14, color='white')
plt.grid(True, alpha=0.3, axis='x')

# Add legend
private_patch = Rectangle((0,0),1,1, fc='gold', alpha=0.8)
public_patch = Rectangle((0,0),1,1, fc='lightblue', alpha=0.8)
plt.legend([private_patch, public_patch], ['Private', 'Public'], loc='lower right')

plt.tight_layout()
plt.savefig('top_10_longest_vacation.png', dpi=300, bbox_inches='tight', facecolor='black')
# plt.show()

# Print summary statistics
print("\n" + "="*50)
print("SUMMARY STATISTICS")
print("="*50)
print(f"Total schools analyzed: {len(df_clean)}")
print(f"Average vacation length: {avg_vacation:.1f} days")
print(f"Median vacation length: {median_vacation:.1f} days")
print(f"Longest vacation: {df_clean['summer_vacation_length_in_days'].max():.0f} days")
print(f"Shortest vacation: {df_clean['summer_vacation_length_in_days'].min():.0f} days")

print("\nBy City:")
print(city_stats)

print("\nBy School Type:")
print(public_private_stats)

print("\nTop 10 Schools with Longest Vacation:")
for i, (idx, row) in enumerate(top_10.iterrows(), 1):
    print(f"{i:2d}. {row['school_name']} ({row['city']}, {row['public_or_private']}) - {row['summer_vacation_length_in_days']:.0f} days")