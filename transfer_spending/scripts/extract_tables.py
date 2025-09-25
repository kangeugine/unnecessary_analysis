#!/usr/bin/env python3
import os
import re
import csv
from bs4 import BeautifulSoup

def clean_text(text):
    """Clean and normalize text content"""
    if not text:
        return ""
    # Remove HTML entities and extra whitespace
    text = re.sub(r'&[^;]+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_monetary_value(text):
    """Extract monetary values from text like '€630.25m' or '€-562.39m'"""
    if not text:
        return ""
    # Remove HTML and get clean text
    text = clean_text(text)
    # Extract the monetary value (with sign if present)
    match = re.search(r'€([-+]?[\d,]+\.?\d*[km]?)', text)
    if match:
        return match.group(1)
    return ""

def extract_club_name(td):
    """Extract club name from the club cell"""
    # Find the link with the club name
    link = td.find('a', title=True)
    if link and link.get('title'):
        return clean_text(link.get('title'))
    return ""

def extract_competition(td):
    """Extract competition name from the competition cell"""
    # Find the link with competition name
    link = td.find('a')
    if link:
        return clean_text(link.get_text())
    return ""

def extract_table_data(html_content):
    """Extract table data from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table
    table = soup.find('table', class_='items')
    if not table:
        return []
    
    rows = []
    tbody = table.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 9:  # Ensure we have enough columns
                row = {}
                
                # Rank
                row['Rank'] = clean_text(tds[0].get_text())
                
                # Club name (from the 3rd td which contains the club link)
                row['Club'] = extract_club_name(tds[2])
                
                # Competition
                row['Competition'] = extract_competition(tds[3])
                
                # Expenditure
                row['Expenditure'] = extract_monetary_value(tds[4].get_text())
                
                # Arrivals
                row['Arrivals'] = clean_text(tds[5].get_text())
                
                # Income
                row['Income'] = extract_monetary_value(tds[6].get_text())
                
                # Departures
                row['Departures'] = clean_text(tds[7].get_text())
                
                # Balance
                row['Balance'] = extract_monetary_value(tds[8].get_text())
                
                rows.append(row)
    
    return rows

def main():
    # Directory containing HTML files
    html_dir = '/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending'
    
    # Get all HTML files
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    html_files.sort()  # Sort to ensure consistent order
    
    all_data = []
    
    # Process each HTML file
    for html_file in html_files:
        print(f"Processing {html_file}...")
        file_path = os.path.join(html_dir, html_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract data from this file
            data = extract_table_data(html_content)
            all_data.extend(data)
            
        except Exception as e:
            print(f"Error processing {html_file}: {e}")
    
    # Write to CSV
    if all_data:
        csv_file = os.path.join(html_dir, 'transfer_spending_data.csv')
        
        fieldnames = ['Rank', 'Club', 'Competition', 'Expenditure', 'Arrivals', 'Income', 'Departures', 'Balance']
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        
        print(f"Successfully extracted {len(all_data)} rows to {csv_file}")
    else:
        print("No data extracted")

if __name__ == "__main__":
    main()