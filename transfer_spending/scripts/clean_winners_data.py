#!/usr/bin/env python3
"""
Script to clean and align winners_combined.csv data with transfer_spending_cleaned.csv format.
"""

import pandas as pd
import os
import re


def map_competition_to_league(competition):
    """Map competition names to league names matching transfer_spending_cleaned.csv."""
    competition_mapping = {
        'Champions League': 'Champions League',  # Keep as is
        'English Premier League': 'Premier League',
        'Spain La Liga': 'LaLiga',
        'France Ligue 1': 'Ligue 1',
        'Italy Serie A': 'Serie A',
        'Germany Bundesliga': 'Bundesliga'
    }
    
    return competition_mapping.get(competition, competition)


def convert_season_format(season):
    """Convert season format from '2024-25' to '24/25'."""
    if pd.isna(season) or season == '':
        return ''
    
    # Handle different season formats
    season_str = str(season).strip()
    
    # Pattern for YYYY-YY format (e.g., "2024-25")
    match = re.match(r'^(\d{4})-(\d{2})$', season_str)
    if match:
        year1, year2 = match.groups()
        return f"{year1[2:]}/{year2}"
    
    # Pattern for YYYY-Y format (e.g., "2008-9", "2007-8")
    match = re.match(r'^(\d{4})-(\d{1})$', season_str)
    if match:
        year1, year2 = match.groups()
        # Convert single digit to two digits with leading zero
        year2_formatted = f"0{year2}"
        return f"{year1[2:]}/{year2_formatted}"
    
    # Pattern for YYYY-YYYY format (e.g., "2024-2025")
    match = re.match(r'^(\d{4})-(\d{4})$', season_str)
    if match:
        year1, year2 = match.groups()
        return f"{year1[2:]}/{year2[2:]}"
    
    # Pattern for YY/YY format (already correct)
    match = re.match(r'^(\d{2})/(\d{2})$', season_str)
    if match:
        return season_str
    
    # Pattern for single year (e.g., "2024")
    match = re.match(r'^(\d{4})$', season_str)
    if match:
        year = int(match.group(1))
        next_year = year + 1
        return f"{str(year)[2:]}/{str(next_year)[2:]}"
    
    # Return as-is if no pattern matches
    return season_str


def calculate_next_season(season):
    """Calculate next season from current season format."""
    if pd.isna(season) or season == '':
        return ''
    
    # Pattern for YY/YY format
    match = re.match(r'^(\d{2})/(\d{2})$', season)
    if match:
        year1, year2 = match.groups()
        next_year1 = int(year2)
        next_year2 = (next_year1 + 1) % 100
        return f"{next_year1:02d}/{next_year2:02d}"
    
    return ''


def map_winner_to_club(winner):
    """Map winner names to club names matching transfer_spending_cleaned.csv."""
    if pd.isna(winner) or winner == '':
        return ''
    
    # Clean up the winner name
    winner = winner.strip()
    
    # Common club name mappings
    club_mapping = {
        # Premier League
        'Manchester United': 'Manchester United',
        'Manchester City': 'Manchester City',
        'Liverpool': 'Liverpool FC',
        'Chelsea': 'Chelsea FC',
        'Arsenal': 'Arsenal FC',
        'Tottenham Hotspur': 'Tottenham Hotspur',
        'Aston Villa': 'Aston Villa',
        'Everton': 'Everton FC',
        'Leicester City': 'Leicester City',
        'Brighton & Hove Albion': 'Brighton & Hove Albion',
        'Newcastle United': 'Newcastle United',
        'West Ham United': 'West Ham United',
        'Burnley': 'Burnley FC',
        'Leeds United': 'Leeds United',
        'Nottingham Forest': 'Nottingham Forest',
        'Blackburn Rovers': 'Blackburn Rovers',
        'Sheffield Wednesday': 'Sheffield Wednesday',
        'Sheffield United': 'Sheffield United',
        'Wolverhampton Wanderers': 'Wolverhampton Wanderers',
        'Huddersfield Town': 'Huddersfield Town',
        'Ipswich Town': 'Ipswich Town',
        'Derby County': 'Derby County',
        'Sunderland': 'Sunderland',
        'Preston North End': 'Preston North End',
        'Portsmouth': 'Portsmouth',
        'West Bromwich Albion': 'West Bromwich Albion',
        
        # LaLiga
        'Real Madrid': 'Real Madrid',
        'Barcelona': 'FC Barcelona',
        'FC Barcelona': 'FC Barcelona',
        'Atletico de Madrid': 'Atlético de Madrid',
        'Atlético Madrid': 'Atlético de Madrid',
        'Atlético de Madrid': 'Atlético de Madrid',
        'Valencia': 'Valencia CF',
        'Sevilla': 'Sevilla FC',
        'Athletic Bilbao': 'Athletic Bilbao',
        'Real Sociedad': 'Real Sociedad',
        'Villarreal': 'Villarreal CF',
        'Betis': 'Real Betis',
        'Deportivo La Coruña': 'Deportivo La Coruña',
        'Espanyol': 'RCD Espanyol',
        
        # Serie A
        'Juventus': 'Juventus FC',
        'Juventus FC': 'Juventus FC',
        'Milan': 'AC Milan',
        'AC Milan': 'AC Milan',
        'Inter Milan': 'Inter Milan',
        'Internazionale': 'Inter Milan',
        'Napoli': 'SSC Napoli',
        'SSC Napoli': 'SSC Napoli',
        'Roma': 'AS Roma',
        'AS Roma': 'AS Roma',
        'Lazio': 'Lazio',
        'Fiorentina': 'Fiorentina',
        'Atalanta': 'Atalanta BC',
        'Torino': 'Torino FC',
        'Genoa': 'Genoa CFC',
        'Sampdoria': 'Sampdoria',
        'Bologna': 'Bologna FC',
        'Cagliari': 'Cagliari',
        'Hellas Verona': 'Hellas Verona',
        'Parma': 'AC Parma',
        
        # Ligue 1
        'Paris Saint-Germain': 'Paris Saint-Germain',
        'Paris Saint-Germain FC': 'Paris Saint-Germain',
        'Olympique de Marseille': 'Olympique de Marseille',
        'Olympique Lyonnais': 'Olympique Lyonnais',
        'AS Monaco': 'AS Monaco',
        'AS Monaco FC': 'AS Monaco',
        'Lille OSC': 'Lille OSC',
        'Lille': 'Lille OSC',
        'FC Nantes': 'FC Nantes',
        'Nantes': 'FC Nantes',
        'Girondins de Bordeaux': 'FC Girondins de Bordeaux',
        'FC Girondins de Bordeaux': 'FC Girondins de Bordeaux',
        'AS Saint-Etienne': 'AS Saint-Etienne',
        'Stade de Reims': 'Stade de Reims',
        'OGC Nice': 'OGC Nice',
        'Nice': 'OGC Nice',
        'RC Lens': 'RC Lens',
        'Lens': 'RC Lens',
        'Montpellier': 'Montpellier',
        'AJ Auxerre': 'AJ Auxerre',
        'RC Strasbourg': 'RC Strasbourg',
        'Strasbourg': 'RC Strasbourg',
        
        # Bundesliga
        'Bayern Munich': 'Bayern Munich',
        'Borussia Dortmund': 'Borussia Dortmund',
        'RB Leipzig': 'RB Leipzig',
        'Bayer Leverkusen': 'Bayer Leverkusen',
        'Borussia Mönchengladbach': 'Borussia Mönchengladbach',
        'Eintracht Frankfurt': 'Eintracht Frankfurt',
        'VfL Wolfsburg': 'VfL Wolfsburg',
        'FC Schalke 04': 'FC Schalke 04',
        'Werder Bremen': 'Werder Bremen',
        'Hamburger SV': 'Hamburger SV',
        'VfB Stuttgart': 'VfB Stuttgart',
        'Hertha Berlin': 'Hertha Berlin',
        'TSG Hoffenheim': 'TSG Hoffenheim',
        'FC Augsburg': 'FC Augsburg',
        'SC Freiburg': 'SC Freiburg',
        'Mainz 05': 'Mainz 05',
        'FC Cologne': 'FC Cologne',
        'Union Berlin': 'Union Berlin',
        'Arminia Bielefeld': 'Arminia Bielefeld',
        'Fortuna Düsseldorf': 'Fortuna Düsseldorf',
        'Paderborn': 'Paderborn',
        'Greuther Fürth': 'Greuther Fürth',
        'Kaiserslautern': 'Kaiserslautern',
        'Nürnberg': 'Nürnberg',
        'Hamburg': 'Hamburger SV',
        'Kaiserslautern': 'Kaiserslautern',
        'Stuttgart': 'VfB Stuttgart',
        'Köln': 'FC Cologne',
        'Mönchengladbach': 'Borussia Mönchengladbach',
        'Frankfurt': 'Eintracht Frankfurt',
        'Dortmund': 'Borussia Dortmund',
        'München': 'Bayern Munich',
        'Leverkusen': 'Bayer Leverkusen',
        'Wolfsburg': 'VfL Wolfsburg',
        'Schalke': 'FC Schalke 04',
        'Bremen': 'Werder Bremen',
        'Hoffenheim': 'TSG Hoffenheim',
        'Augsburg': 'FC Augsburg',
        'Freiburg': 'SC Freiburg',
        'Mainz': 'Mainz 05',
        'Berlin': 'Hertha Berlin',
        'Bielefeld': 'Arminia Bielefeld',
        'Düsseldorf': 'Fortuna Düsseldorf',
        'Fürth': 'Greuther Fürth',
        'Nürnberg': 'Nürnberg',
        
        # Other clubs that might appear in Champions League
        'Porto': 'FC Porto',
        'Benfica': 'SL Benfica',
        'Sporting CP': 'Sporting CP',
        'Ajax': 'Ajax Amsterdam',
        'PSV': 'PSV Eindhoven',
        'Feyenoord': 'Feyenoord',
        'Celtic': 'Celtic FC',
        'Rangers': 'Rangers FC',
        'Dynamo Kiev': 'Dynamo Kiev',
        'Shakhtar Donetsk': 'Shakhtar Donetsk',
        'Galatasaray': 'Galatasaray',
        'Fenerbahce': 'Fenerbahce',
        'Besiktas': 'Besiktas',
        'Olympiakos': 'Olympiakos',
        'Panathinaikos': 'Panathinaikos',
        'Red Star Belgrade': 'Red Star Belgrade',
        'Partizan': 'Partizan Belgrade',
        'Steaua Bucureşti': 'Steaua Bucureşti',
        'Dynamo Bucharest': 'Dynamo Bucharest',
        'Marseille': 'Olympique de Marseille',
        'Club Brugge': 'Club Brugge',
        'Anderlecht': 'Anderlecht',
        'Malmö FF': 'Malmö FF',
        'Rosenborg': 'Rosenborg',
        'CSKA Moscow': 'CSKA Moscow',
        'Spartak Moscow': 'Spartak Moscow',
        'Zenit St Petersburg': 'Zenit St Petersburg',
        'Borussia Mönchengladbach': 'Borussia Mönchengladbach',
        'Saint-Etienne': 'AS Saint-Etienne',
        'Leeds United': 'Leeds United',
        'Monaco': 'AS Monaco',
        'Stade de Reims': 'Stade de Reims',
        'FC Sete': 'FC Sete',
        'FC Sochaux-Montbeliard': 'FC Sochaux-Montbeliard',
        'Racing Club de Paris': 'Racing Club de Paris',
        'Olympique Lillois': 'Olympique Lillois',
        'CO Roubaix-Tourcoing': 'CO Roubaix-Tourcoing',
        'Burnley Wolverhampton': 'Burnley FC',  # Possible data error
    }
    
    # Try exact match first
    if winner in club_mapping:
        return club_mapping[winner]
    
    # Try partial matches for some common variations
    for key, value in club_mapping.items():
        if key.lower() in winner.lower() or winner.lower() in key.lower():
            return value
    
    # If no mapping found, return the original name
    return winner


def main():
    """Main function to clean and align winners data."""
    # Define paths
    data_dir = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/data'
    input_file = os.path.join(data_dir, 'winners_combined.csv')
    output_file = os.path.join(data_dir, 'winners_cleaned.csv')
    
    # Load the data
    print("Loading winners_combined.csv...")
    df = pd.read_csv(input_file)
    
    print(f"Original data shape: {df.shape}")
    print(f"Original columns: {list(df.columns)}")
    
    # Create new columns
    print("\nProcessing data...")
    
    # 1. Map Competition to League
    print("  - Mapping Competition to League...")
    df['League'] = df['Competition'].apply(map_competition_to_league)
    
    # 2. Convert Season format
    print("  - Converting Season format...")
    df['Winning Season'] = df['Season'].apply(convert_season_format)
    
    # 3. Calculate Next Season
    print("  - Calculating Next Season...")
    df['Next Season'] = df['Winning Season'].apply(calculate_next_season)
    
    # 4. Map Winner to Club
    print("  - Mapping Winner to Club...")
    df['Club'] = df['Winner'].apply(map_winner_to_club)
    
    # Select and reorder columns
    final_columns = [
        'League', 'Winning Season', 'Next Season', 'Club', 
        'Runner_up', 'Score', 'Competition', 'Season', 'Winner'
    ]
    df = df[final_columns]
    
    # Save the cleaned data
    print(f"\nSaving cleaned data to {output_file}...")
    df.to_csv(output_file, index=False)
    
    print(f"\nResults:")
    print(f"  - Final data shape: {df.shape}")
    print(f"  - Final columns: {list(df.columns)}")
    
    # Show preview
    print(f"\nPreview of cleaned data:")
    print(df.head(10))
    
    # Show unique values in key columns
    print(f"\nUnique Leagues: {sorted(df['League'].unique())}")
    print(f"Sample Winning Seasons: {sorted(df['Winning Season'].unique())[:10]}")
    print(f"Sample Next Seasons: {sorted(df['Next Season'].unique())[:10]}")
    print(f"Sample Clubs: {sorted(df['Club'].unique())[:10]}")
    
    # Show data by league
    print(f"\nData by League:")
    league_counts = df['League'].value_counts()
    for league, count in league_counts.items():
        print(f"  - {league}: {count} rows")
    
    print(f"\nCleaned data saved successfully!")


if __name__ == "__main__":
    main()