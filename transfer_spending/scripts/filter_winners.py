#!/usr/bin/env python3
"""
Script to filter winners_cleaned.csv to remove seasons before 2000-01.
"""

import pandas as pd
import os
import re


def season_to_year(season):
    """Convert season format to starting year for comparison."""
    if pd.isna(season) or season == '':
        return None
    
    # Handle YY/YY format
    match = re.match(r'^(\d{2})/(\d{2})$', season)
    if match:
        year1 = int(match.group(1))
        # Convert 2-digit year to 4-digit year
        # 00-25 -> 2000-2025, 26-99 -> 1926-1999
        if year1 <= 25:
            return 2000 + year1
        else:
            return 1900 + year1
    
    return None


def main():
    """Main function to filter winners data."""
    # Define paths
    data_dir = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data'
    input_file = os.path.join(data_dir, 'winners_cleaned.csv')
    output_file = os.path.join(data_dir, 'winners_cleaned_filtered.csv')
    
    # Load the data
    print("Loading winners_cleaned.csv...")
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    
    # Show sample of original data
    print(f"\nSample of original data:")
    print(df[['League', 'Winning Season', 'Next Season', 'Club']].head(10))
    
    # Convert seasons to years for filtering
    df['season_year'] = df['Winning Season'].apply(season_to_year)
    
    # Filter to keep seasons from 2000-01 onwards (starting year >= 2000)
    print(f"\nFiltering to keep seasons from 2000-01 onwards...")
    filtered_df = df[df['season_year'] >= 2000].copy()
    
    # Drop the helper column
    filtered_df = filtered_df.drop('season_year', axis=1)
    
    print(f"Filtered data shape: {filtered_df.shape}")
    print(f"Removed {len(df) - len(filtered_df)} rows")
    
    # Show sample of filtered data
    print(f"\nSample of filtered data:")
    print(filtered_df[['League', 'Winning Season', 'Next Season', 'Club']].head(10))
    
    # Show data by league
    print(f"\nData by league (after filtering):")
    league_counts = filtered_df['League'].value_counts()
    for league, count in league_counts.items():
        print(f"  - {league}: {count} rows")
    
    # Show season range by league
    print(f"\nSeason range by league:")
    for league in sorted(filtered_df['League'].unique()):
        league_data = filtered_df[filtered_df['League'] == league]
        min_season = league_data['Winning Season'].min()
        max_season = league_data['Winning Season'].max()
        print(f"  - {league}: {min_season} to {max_season}")
    
    # Save filtered data
    print(f"\nSaving filtered data to {output_file}...")
    filtered_df.to_csv(output_file, index=False)
    
    print(f"Filtering completed successfully!")


if __name__ == "__main__":
    main()