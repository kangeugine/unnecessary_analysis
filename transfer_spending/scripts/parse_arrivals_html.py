#!/usr/bin/env python3
"""
Script to parse HTML files from transfer_spending/html/arrivals/ directory
and convert them to CSV files.

Each HTML file contains a table with player transfer information including:
- Player name
- Position  
- Age
- Nationality
- Previous club
- Transfer fee
"""

import os
import re
import csv
from pathlib import Path
from bs4 import BeautifulSoup


def extract_text_clean(element):
    """Extract clean text from BeautifulSoup element, handling None values"""
    if element is None:
        return ""
    return element.get_text(strip=True)


def parse_fee(fee_text):
    """Parse transfer fee text to extract numerical value"""
    if not fee_text or fee_text == "-":
        return "Free"
    
    # Handle loan end cases
    if "End of loan" in fee_text:
        return "End of loan"
    
    # Extract fee amount (e.g., "€94.00m" -> "94.00")
    fee_match = re.search(r'€([\d.]+)([mk]?)', fee_text)
    if fee_match:
        amount = fee_match.group(1)
        unit = fee_match.group(2)
        if unit == 'm':
            return f"{amount}m"
        elif unit == 'k':
            return f"{amount}k" 
        else:
            return amount
    
    return fee_text


def extract_club_and_league(club_cell):
    """Extract club name and league from the club cell"""
    if not club_cell:
        return "", ""
    
    # Find the club name link
    club_link = club_cell.find('a', {'title': True})
    club_name = club_link.get('title', '') if club_link else ""
    
    # Find league information
    league_link = club_cell.find('a', href=lambda x: x and '/transfers/wettbewerb/' in x)
    league = league_link.get_text(strip=True) if league_link else ""
    
    return club_name, league


def extract_nationality(nat_cell):
    """Extract nationality from nationality cell (may have multiple flags)"""
    if not nat_cell:
        return ""
    
    # Find all flag images
    flags = nat_cell.find_all('img', {'title': True})
    nationalities = [flag.get('title', '') for flag in flags if flag.get('title')]
    
    return " / ".join(nationalities)


def parse_player_row(row, debug=False):
    """Parse a single player row from the HTML table"""
    cells = row.find_all('td')
    if len(cells) < 6:
        return None
    
    # Extract player name from cell 1 (nested table)
    player_cell = cells[1]
    player_link = player_cell.find('a', {'title': True})
    player_name = player_link.get('title', '') if player_link else ""
    
    # Position is also in cell 1 but in second row of nested table
    position_cells = player_cell.find_all('td')
    position = ""
    for cell in position_cells:
        text = cell.get_text(strip=True)
        # Look for position text (not player name link)
        if text and not cell.find('a') and text != player_name:
            position = text
            break
    
    # For 12-cell structure (like Real Madrid):
    if len(cells) >= 12:
        # Age (cell 5)
        age = extract_text_clean(cells[5])
        
        # Nationality (cell 6) - need to check for flags
        nat_cell = cells[6]
        if not nat_cell.get_text(strip=True):
            # Try next cell that might have nationality flags
            for i in range(6, min(len(cells), 10)):
                if cells[i].find('img', {'title': True}):
                    nat_cell = cells[i]
                    break
        nationality = extract_nationality(nat_cell)
        
        # Previous club info (cell 7 or later)
        club_cell = cells[7]  
        previous_club, previous_league = extract_club_and_league(club_cell)
        
        # Transfer fee (last cell)
        fee_cell = cells[-1]
        fee_link = fee_cell.find('a')
        fee_text = extract_text_clean(fee_link) if fee_link else extract_text_clean(fee_cell)
        transfer_fee = parse_fee(fee_text)
        
    else:
        # For 6-cell structure (standard):
        # Age (cell 2)
        age = extract_text_clean(cells[2])
        
        # Nationality (cell 3)
        nationality = extract_nationality(cells[3])
        
        # Previous club and league (cell 4)
        previous_club, previous_league = extract_club_and_league(cells[4])
        
        # Transfer fee (cell 5)
        fee_cell = cells[5]
        fee_link = fee_cell.find('a')
        fee_text = extract_text_clean(fee_link) if fee_link else extract_text_clean(fee_cell)
        transfer_fee = parse_fee(fee_text)
    
    return {
        'player_name': player_name,
        'position': position,
        'age': age,
        'nationality': nationality,
        'previous_club': previous_club,
        'previous_league': previous_league,
        'transfer_fee': transfer_fee
    }


def extract_summary_info(soup):
    """Extract summary information from table footer"""
    tfoot = soup.find('tfoot')
    if not tfoot:
        return {}, "", ""
    
    summary_info = {}
    tfoot_text = tfoot.get_text()
    
    # Extract total sum
    sum_match = re.search(r'Sum: €([\d.]+[mk]?)', tfoot_text)
    if sum_match:
        summary_info['total_spent'] = sum_match.group(1)
    
    # Extract average age
    age_match = re.search(r'Average age: ([\d.]+)', tfoot_text)
    if age_match:
        summary_info['average_age'] = age_match.group(1)
    
    # Extract total market value
    value_match = re.search(r'Total market value of arrivals: €([\d.]+[mk]?)', tfoot_text)
    if value_match:
        summary_info['total_market_value'] = value_match.group(1)
    
    return summary_info


def parse_club_season_from_filename(filename):
    """Extract club name and season from filename"""
    # Remove .html extension
    base_name = filename.replace('.html', '')
    
    # Split by last underscore to separate season
    parts = base_name.rsplit('_', 1)
    if len(parts) == 2:
        club_name = parts[0].replace('_', ' ').title()
        season = parts[1]
        
        # Format season (e.g., "1718" -> "2017-18")
        if len(season) == 4:
            season_formatted = f"20{season[:2]}-{season[2:]}"
        else:
            season_formatted = season
        
        return club_name, season_formatted
    
    return base_name.replace('_', ' ').title(), ""


def parse_html_file(html_path, output_dir):
    """Parse a single HTML file and save as CSV"""
    print(f"Processing: {html_path.name}")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the main table
        table = soup.find('table', class_='items')
        if not table:
            print(f"  Warning: No table found in {html_path.name}")
            return
        
        # Extract club and season from filename
        club_name, season = parse_club_season_from_filename(html_path.name)
        
        # Extract summary information
        summary_info = extract_summary_info(soup)
        
        # Find all player rows in tbody
        tbody = table.find('tbody')
        if not tbody:
            print(f"  Warning: No tbody found in {html_path.name}")
            return
        
        rows = tbody.find_all('tr')
        players = []
        
        for row in rows:
            player_data = parse_player_row(row)
            if player_data:
                # Add club and season info to each player
                player_data['club'] = club_name
                player_data['season'] = season
                players.append(player_data)
        
        if not players:
            print(f"  Warning: No players found in {html_path.name}")
            return
        
        # Debug: Print first player data for testing
        # if html_path.name == 'real_madrid_0910.html':
        #     print(f"  Debug - First player: {players[0]}")
        
        # Create CSV filename
        csv_filename = html_path.stem + '.csv'
        csv_path = output_dir / csv_filename
        
        # Write to CSV
        fieldnames = ['club', 'season', 'player_name', 'position', 'age', 'nationality', 
                     'previous_club', 'previous_league', 'transfer_fee']
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(players)
        
        print(f"  ✓ Saved {len(players)} players to {csv_filename}")
        
        # Print summary info
        if summary_info:
            print(f"  Summary: Total spent: {summary_info.get('total_spent', 'N/A')}, "
                  f"Avg age: {summary_info.get('average_age', 'N/A')}, "
                  f"Market value: {summary_info.get('total_market_value', 'N/A')}")
    
    except Exception as e:
        print(f"  Error processing {html_path.name}: {str(e)}")


def main():
    """Main function to process all HTML files in arrivals directory"""
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    html_dir = project_root / 'html' / 'arrivals'
    data_dir = project_root / 'data'
    
    # Create arrivals subdirectory in data folder
    arrivals_data_dir = data_dir / 'arrivals'
    arrivals_data_dir.mkdir(exist_ok=True)
    
    # Check if HTML directory exists
    if not html_dir.exists():
        print(f"Error: HTML directory not found at {html_dir}")
        return
    
    # Get all HTML files
    html_files = list(html_dir.glob('*.html'))
    
    if not html_files:
        print(f"No HTML files found in {html_dir}")
        return
    
    print(f"Found {len(html_files)} HTML files to process")
    print(f"Output directory: {arrivals_data_dir}")
    print("-" * 50)
    
    # Process each HTML file
    for html_file in sorted(html_files):
        parse_html_file(html_file, arrivals_data_dir)
    
    print("-" * 50)
    print(f"Processing complete! CSV files saved to {arrivals_data_dir}")


if __name__ == "__main__":
    main()