#!/usr/bin/env python3
import pandas as pd
import re

def split_competition(competition_str):
    """
    Split competition string into league and season components.
    
    Args:
        competition_str (str): Competition string like "Premier League 22/23"
        
    Returns:
        tuple: (league, season) where league is the league name and season is the season code
    """
    if not competition_str or not isinstance(competition_str, str):
        return "", ""
    
    # Clean up the string first
    competition_str = competition_str.strip()
    
    # Pattern to match season format: digits/digits at the end (with optional whitespace)
    season_pattern = r'\s+(\d{2}/\d{2})\s*$'
    
    # Search for season pattern
    match = re.search(season_pattern, competition_str)
    
    if match:
        season = match.group(1)
        league = competition_str[:match.start()].strip()
        return league, season
    else:
        # If no season pattern found, treat entire string as league
        return competition_str.strip(), ""

def clean_transfer_data(input_file, output_file):
    """
    Clean the transfer spending CSV by splitting Competition into League and Season.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Split the Competition column
    df[['League', 'Season']] = df['Competition'].apply(
        lambda x: pd.Series(split_competition(x))
    )
    
    # Reorder columns to put League and Season after Competition
    cols = df.columns.tolist()
    
    # Remove League and Season from their current position
    cols = [col for col in cols if col not in ['League', 'Season']]
    
    # Find the index of Competition column
    comp_index = cols.index('Competition')
    
    # Insert League and Season after Competition
    cols.insert(comp_index + 1, 'League')
    cols.insert(comp_index + 2, 'Season')
    
    # Reorder the dataframe
    df = df[cols]
    
    # Save the cleaned data
    df.to_csv(output_file, index=False)
    
    print(f"Successfully cleaned data and saved to {output_file}")
    print(f"Total rows processed: {len(df)}")
    
    # Show some sample data
    print("\nSample of cleaned data:")
    print(df[['Competition', 'League', 'Season']].head(10))

if __name__ == "__main__":
    input_file = "/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/transfer_spending_data.csv"
    output_file = "/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/transfer_spending_cleaned.csv"
    
    clean_transfer_data(input_file, output_file)