#!/usr/bin/env python3
"""
Script to parse HTML tables from winners files and combine them into a single CSV file.
"""

import os
import pandas as pd
from bs4 import BeautifulSoup
import glob


def parse_html_table(html_file_path):
    """Parse HTML table from a winners file and return a DataFrame."""
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    if not table:
        print(f"No table found in {html_file_path}")
        return None
    
    # Extract table headers
    headers = []
    header_row = table.find('tr')
    if header_row:
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.get_text(strip=True))
    
    # Extract table data
    data = []
    rows = table.find_all('tr')[1:]  # Skip header row
    
    for row in rows:
        cols = row.find_all(['td', 'th'])
        row_data = []
        for col in cols:
            # Clean up text by removing extra whitespace and links
            text = col.get_text(strip=True)
            # Remove any URLs or extra formatting
            text = text.replace('\n', ' ').replace('\t', ' ')
            # Handle multiple spaces
            text = ' '.join(text.split())
            row_data.append(text)
        
        if row_data:  # Only add non-empty rows
            data.append(row_data)
    
    # Create DataFrame
    if headers and data:
        # Ensure all rows have the same number of columns as headers
        max_cols = len(headers)
        for i, row in enumerate(data):
            if len(row) < max_cols:
                data[i].extend([''] * (max_cols - len(row)))
            elif len(row) > max_cols:
                data[i] = row[:max_cols]
        
        df = pd.DataFrame(data, columns=headers)
        
        # Add source file information
        file_name = os.path.basename(html_file_path)
        competition = file_name.replace('_winners.html', '').replace('_', ' ').title()
        
        # Normalize column names based on competition type
        if 'champions_league' in html_file_path:
            # Champions League has Season, Winners, Runners-up, Score
            df = df.rename(columns={
                'Season ': 'Season',
                'Season': 'Season',
                'Winners': 'Winner',
                'Runners-up': 'Runner_up',
                'Score': 'Score'
            })
            df['Competition'] = 'Champions League'
        elif any(league in html_file_path for league in ['premier_league', 'la_liga', 'serie_a', 'ligue_1']):
            # League tables have Year and Winner (with different column names)
            year_col = None
            winner_col = None
            
            # Find year column
            for col in df.columns:
                if 'Year' in col or 'year' in col:
                    year_col = col
                    break
            if not year_col:
                year_col = df.columns[0]
            
            # Find winner column
            for col in df.columns:
                if col != year_col and any(word in col for word in ['Champion', 'League', 'Division']):
                    winner_col = col
                    break
            if not winner_col and len(df.columns) > 1:
                winner_col = df.columns[1]
            
            if year_col and winner_col:
                df = df.rename(columns={
                    year_col: 'Season',
                    winner_col: 'Winner'
                })
            
            df['Competition'] = competition
            df['Runner_up'] = ''
            df['Score'] = ''
        
        # Keep only the standardized columns
        standard_cols = ['Competition', 'Season', 'Winner', 'Runner_up', 'Score']
        for col in standard_cols:
            if col not in df.columns:
                df[col] = ''
        
        df = df[standard_cols]
        
        return df
    
    return None


def main():
    # Define paths
    html_dir = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/html'
    data_dir = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data'
    
    # Find all *_winners.html files
    winners_files = glob.glob(os.path.join(html_dir, '*_winners.html'))
    
    if not winners_files:
        print("No *_winners.html files found!")
        return
    
    print(f"Found {len(winners_files)} winners files:")
    for file in winners_files:
        print(f"  - {os.path.basename(file)}")
    
    # Parse all files and combine data
    all_dataframes = []
    
    for html_file in winners_files:
        print(f"\nProcessing {os.path.basename(html_file)}...")
        df = parse_html_table(html_file)
        
        if df is not None:
            print(f"  - Extracted {len(df)} rows")
            all_dataframes.append(df)
        else:
            print(f"  - Failed to parse {html_file}")
    
    if not all_dataframes:
        print("No data extracted from any files!")
        return
    
    # Combine all DataFrames
    print(f"\nCombining data from {len(all_dataframes)} files...")
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Clean up data
    combined_df = combined_df.fillna('')
    
    # Filter out rows with no meaningful data
    combined_df = combined_df[combined_df['Winner'].str.strip() != '']
    combined_df = combined_df[~combined_df['Winner'].str.contains('No football league', case=False, na=False)]
    combined_df = combined_df[~combined_df['Winner'].str.contains('No Champion', case=False, na=False)]
    
    # Clean up season/year formatting
    combined_df['Season'] = combined_df['Season'].str.replace('–', '-')
    
    # Save to CSV
    output_file = os.path.join(data_dir, 'winners_combined.csv')
    combined_df.to_csv(output_file, index=False)
    
    print(f"\nResults:")
    print(f"  - Total rows: {len(combined_df)}")
    print(f"  - Total columns: {len(combined_df.columns)}")
    print(f"  - Columns: {list(combined_df.columns)}")
    print(f"  - Output file: {output_file}")
    
    # Show first few rows as preview
    print(f"\nPreview of combined data:")
    print(combined_df.head(10))
    
    # Show competition breakdown
    print(f"\nData by competition:")
    competition_counts = combined_df['Competition'].value_counts()
    for comp, count in competition_counts.items():
        print(f"  - {comp}: {count} rows")


if __name__ == "__main__":
    main()