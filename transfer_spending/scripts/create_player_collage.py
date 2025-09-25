#!/usr/bin/env python3
"""
Football Player Collage Creator
Downloads player images and creates a collage with names below pictures
"""

import os
import requests
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
from io import BytesIO
import time

def search_and_download_player_image(player_name, images_dir):
    """
    Download player image from predefined high-quality sources
    """
    # Create a safe filename
    safe_name = "".join(c for c in player_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{safe_name}.jpg"
    filepath = os.path.join(images_dir, filename)
    
    # Check if image already exists
    if os.path.exists(filepath):
        print(f"Using existing image for {player_name}")
        return filepath
    
    # Predefined image URLs for the players (using Wikipedia commons)
    player_images = {
        "Cristiano Ronaldo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Cristiano_Ronaldo_2018.jpg/800px-Cristiano_Ronaldo_2018.jpg",
        "Kaká": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Kaka_2009.jpg/800px-Kaka_2009.jpg", 
        "Karim Benzema": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Karim_Benzema_2018.jpg/800px-Karim_Benzema_2018.jpg",
        "Xabi Alonso": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Xabi_Alonso_2014.jpg/800px-Xabi_Alonso_2014.jpg"
    }
    
    try:
        if player_name in player_images:
            url = player_images[player_name]
            print(f"Downloading image for {player_name} from Wikipedia...")
            
            # Download the image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Open and process the image
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize image to standard size
            img = img.resize((300, 400), Image.Resampling.LANCZOS)
            
            # Save the image
            img.save(filepath, 'JPEG', quality=85)
            print(f"Successfully downloaded and saved image for {player_name}")
            return filepath
        else:
            print(f"No predefined image URL for {player_name}, creating placeholder")
            create_placeholder_image(player_name, filepath)
            return filepath
            
    except Exception as e:
        print(f"Error downloading image for {player_name}: {e}")
        # Create placeholder as fallback
        create_placeholder_image(player_name, filepath)
        return filepath

def create_placeholder_image(player_name, filepath):
    """
    Create a placeholder image with player name
    """
    img = Image.new('RGB', (300, 400), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = f"Photo of\n{player_name}"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (300 - text_width) // 2
    y = (400 - text_height) // 2
    draw.multiline_text((x, y), text, fill='white', font=font, align='center')
    
    img.save(filepath)
    print(f"Created placeholder image for {player_name}")

def create_collage(player_names, images_dir, output_path):
    """
    Create a collage of player images with names below
    """
    # Download images for all players
    image_paths = []
    for player in player_names:
        img_path = search_and_download_player_image(player, images_dir)
        image_paths.append((img_path, player))
    
    # Create collage layout (2x2 grid for 4 players)
    img_width, img_height = 300, 400
    text_height = 50
    cols = 2
    rows = 2
    
    collage_width = cols * img_width
    collage_height = rows * (img_height + text_height)
    
    # Create blank collage canvas
    collage = Image.new('RGB', (collage_width, collage_height), 'white')
    
    # Load font for names
    try:
        name_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        name_font = ImageFont.load_default()
    
    # Place images and names in grid
    for i, (img_path, player_name) in enumerate(image_paths):
        row = i // cols
        col = i % cols
        
        # Calculate position
        x = col * img_width
        y = row * (img_height + text_height)
        
        # Open and resize image
        with Image.open(img_path) as img:
            img = img.resize((img_width, img_height))
            collage.paste(img, (x, y))
        
        # Add player name below image
        draw = ImageDraw.Draw(collage)
        name_bbox = draw.textbbox((0, 0), player_name, font=name_font)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = x + (img_width - name_width) // 2
        name_y = y + img_height + 10
        
        draw.text((name_x, name_y), player_name, fill='black', font=name_font)
    
    # Save collage
    collage.save(output_path)
    print(f"Collage saved to {output_path}")
    return output_path

def main():
    # Player names
    players = [
        "Cristiano Ronaldo",
        "Kaká", 
        "Karim Benzema",
        "Xabi Alonso"
    ]
    
    # Directories
    base_dir = "/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending"
    images_dir = os.path.join(base_dir, "images")
    output_path = os.path.join(images_dir, "football_players_collage.jpg")
    
    # Create images directory if it doesn't exist
    os.makedirs(images_dir, exist_ok=True)
    
    print("Creating football player collage...")
    print(f"Players: {', '.join(players)}")
    
    # Create collage
    create_collage(players, images_dir, output_path)
    
    print("\nCollage creation complete!")
    print(f"Individual images saved in: {images_dir}")
    print(f"Final collage saved as: {output_path}")

if __name__ == "__main__":
    main()