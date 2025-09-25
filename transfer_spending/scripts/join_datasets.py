#!/usr/bin/env python3
"""
Script to join transfer_spending_cleaned.csv and winners_cleaned.csv datasets.
"""

import pandas as pd
import os


def main():
    """Main function to join the datasets."""
    # Define paths
    data_dir = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data'
    transfer_file = os.path.join(data_dir, 'transfer_spending_cleaned.csv')
    winners_file = os.path.join(data_dir, 'winners_cleaned.csv')
    output_file = os.path.join(data_dir, 'transfer_spending_with_winners.csv')
    
    # Load the datasets
    print("Loading datasets...")
    transfer_df = pd.read_csv(transfer_file)
    winners_df = pd.read_csv(winners_file)
    
    print(f"Transfer spending data shape: {transfer_df.shape}")
    print(f"Winners data shape: {winners_df.shape}")
    
    # Display column names to verify
    print(f"\nTransfer spending columns: {list(transfer_df.columns)}")
    print(f"Winners columns: {list(winners_df.columns)}")
    
    # Display unique leagues in both datasets
    print(f"\nUnique leagues in transfer spending: {sorted(transfer_df['League'].unique())}")
    print(f"Unique leagues in winners: {sorted(winners_df['League'].unique())}")
    
    # Prepare winners data for joining
    # Keep only League, Next Season, and Club columns, rename Club to Winning Club
    winners_join = winners_df[['League', 'Winning Season', 'Next Season', 'Club']].copy()
    winners_join = winners_join.rename(columns={'Club': 'Winning Club'})
    
    # Filter out rows with empty Next Season (these are the most recent seasons)
    winners_join = winners_join[winners_join['Next Season'] != '']
    
    # Filter to keep only seasons from 2000-01 onwards
    def season_to_year(season):
        """Convert season format to starting year for comparison."""
        if pd.isna(season) or season == '':
            return None
        
        # Handle YY/YY format
        import re
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
    
    # Filter to keep seasons from 2000-01 onwards (starting year >= 2000)
    winners_join['season_year'] = winners_join['Winning Season'].apply(season_to_year)
    winners_join = winners_join[winners_join['season_year'] >= 2000]
    winners_join = winners_join.drop('season_year', axis=1)
    
    # Remove any remaining duplicates by keeping the first occurrence
    winners_join = winners_join.drop_duplicates(subset=['League', 'Next Season'], keep='first')
    
    print(f"\nWinners data for joining shape (after filtering to 2000+ seasons): {winners_join.shape}")
    print(f"Sample winners data:")
    print(winners_join.head())
    
    # Check for any remaining duplicates
    duplicates = winners_join[winners_join.duplicated(subset=['League', 'Next Season'], keep=False)]
    if len(duplicates) > 0:
        print(f"\nWarning: Found {len(duplicates)} duplicate League/Next Season combinations:")
        print(duplicates[['League', 'Next Season', 'Winning Club']].head(10))
    else:
        print(f"\nNo duplicate League/Next Season combinations found after filtering.")
    
    # Perform the first join
    # Join transfer_spending_cleaned.csv on (League, Season) 
    # with winners_cleaned.csv on (League, Next Season)
    print(f"\nPerforming first join (League + Season winners)...")
    joined_df = pd.merge(
        transfer_df, 
        winners_join, 
        left_on=['League', 'Season'], 
        right_on=['League', 'Next Season'], 
        how='left'
    )
    
    # Drop the duplicate Next Season column since we joined on it
    joined_df = joined_df.drop('Next Season', axis=1)
    
    print(f"First join completed. Shape: {joined_df.shape}")
    
    # Prepare Champions League winners data for second join
    print(f"\nPreparing Champions League winners data...")
    
    # Filter Champions League winners and keep only Next Season and Club columns
    champions_data = winners_df[winners_df['League'] == 'Champions League'][['Next Season', 'Club']].copy()
    
    # Filter to 2000+ seasons using the same logic
    champions_data['season_year'] = champions_data['Next Season'].apply(lambda x: season_to_year(x) if pd.notna(x) and x != '' else None)
    champions_data = champions_data[champions_data['season_year'] >= 2000]
    champions_data = champions_data.drop('season_year', axis=1)
    
    # Remove empty Next Season rows
    champions_data = champions_data[champions_data['Next Season'] != '']
    
    # Rename Club to Champions League Winners
    champions_data = champions_data.rename(columns={'Club': 'Champions League Winners'})
    
    # Remove duplicates
    champions_data = champions_data.drop_duplicates(subset=['Next Season'], keep='first')
    
    print(f"Champions League data shape: {champions_data.shape}")
    print(f"Sample Champions League data:")
    print(champions_data.head())
    
    # Perform the second join
    # Join the result of first join with Champions League winners on Season = Next Season
    print(f"\nPerforming second join (Champions League winners)...")
    final_df = pd.merge(
        joined_df,
        champions_data,
        left_on='Season',
        right_on='Next Season',
        how='left'
    )
    
    # Drop the duplicate Next Season column
    final_df = final_df.drop('Next Season', axis=1)
    
    print(f"Final joined data shape: {final_df.shape}")
    print(f"Final columns: {list(final_df.columns)}")
    
    # Show join statistics
    total_rows = len(final_df)
    domestic_matched = len(final_df[final_df['Winning Club'].notna()])
    champions_matched = len(final_df[final_df['Champions League Winners'].notna()])
    
    print(f"\nJoin statistics:")
    print(f"  - Total rows: {total_rows}")
    print(f"  - Domestic league winners matched: {domestic_matched}")
    print(f"  - Champions League winners matched: {champions_matched}")
    print(f"  - Domestic match rate: {domestic_matched/total_rows*100:.1f}%")
    print(f"  - Champions League match rate: {champions_matched/total_rows*100:.1f}%")
    
    # Show breakdown by league
    print(f"\nMatch rates by league:")
    league_stats = final_df.groupby('League').agg({
        'Winning Club': ['count', lambda x: x.notna().sum()],
        'Champions League Winners': ['count', lambda x: x.notna().sum()]
    }).round(2)
    league_stats.columns = ['Total', 'Domestic_Matched', 'Total2', 'Champions_Matched']
    league_stats = league_stats.drop('Total2', axis=1)
    league_stats['Domestic_Rate_%'] = (league_stats['Domestic_Matched'] / league_stats['Total'] * 100).round(1)
    league_stats['Champions_Rate_%'] = (league_stats['Champions_Matched'] / league_stats['Total'] * 100).round(1)
    print(league_stats)
    
    # Save the final joined dataset
    output_file = os.path.join(data_dir, 'transfer_spending_with_winners.csv')
    print(f"\nSaving final joined dataset to {output_file}...")
    final_df.to_csv(output_file, index=False)
    
    # Show preview of final joined data
    print(f"\nPreview of final joined data:")
    print(final_df[['League', 'Season', 'Club', 'Winning Club', 'Champions League Winners']].head(10))
    
    # Show some examples of Champions League matches
    print(f"\nExamples with Champions League winners:")
    champions_examples = final_df[final_df['Champions League Winners'].notna()][['League', 'Season', 'Club', 'Winning Club', 'Champions League Winners']].head(10)
    if len(champions_examples) > 0:
        print(champions_examples)
    else:
        print("No Champions League winners found in the data")
    
    print(f"\nJoin process completed successfully!")


if __name__ == "__main__":
    main()