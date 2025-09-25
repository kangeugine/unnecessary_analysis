#!/usr/bin/env python3

import os
from PIL import Image

def create_horizontal_collage():
    """Create a horizontal collage from all images in the images folder"""
    
    # Define paths
    images_dir = "../images"
    output_path = "../plots/real_madrid_players_collage.jpg"
    
    # Get all image files
    image_files = []
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_files.append(os.path.join(images_dir, filename))
    
    if not image_files:
        print("No image files found in the images directory")
        return
    
    # Sort files for consistent ordering
    image_files.sort()
    
    # Load and resize images to same height
    images = []
    target_height = 400  # Standard height for all images
    
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            # Calculate width to maintain aspect ratio
            aspect_ratio = img.width / img.height
            target_width = int(target_height * aspect_ratio)
            
            # Resize image
            img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            images.append(img_resized)
            print(f"Loaded: {os.path.basename(img_path)}")
            
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
    
    if not images:
        print("No images could be loaded")
        return
    
    # Calculate total width
    total_width = sum(img.width for img in images)
    
    # Create collage
    collage = Image.new('RGB', (total_width, target_height), 'white')
    
    # Paste images horizontally
    x_offset = 0
    for img in images:
        collage.paste(img, (x_offset, 0))
        x_offset += img.width
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save collage
    collage.save(output_path, quality=95)
    print(f"Horizontal collage saved to: {output_path}")
    print(f"Final dimensions: {collage.width}x{collage.height}")

if __name__ == "__main__":
    create_horizontal_collage()