import os
import math
from PIL import Image
import glob

def get_optimal_grid_size(num_images):
    """Calculate optimal grid dimensions for given number of images"""
    if num_images <= 1:
        return 1, 1
    elif num_images <= 4:
        return 2, 2
    elif num_images <= 6:
        return 2, 3
    elif num_images <= 9:
        return 3, 3
    else:
        # For larger numbers, try to get close to square
        sqrt_n = math.sqrt(num_images)
        cols = math.ceil(sqrt_n)
        rows = math.ceil(num_images / cols)
        return rows, cols

def resize_and_crop_to_fill(image, target_width, target_height):
    """Resize and crop image to fill entire target dimensions while preserving heads"""
    img_width, img_height = image.size
    
    # Calculate scaling factor to fill the entire area
    scale_w = target_width / img_width
    scale_h = target_height / img_height
    scale = max(scale_w, scale_h)  # Use max to fill the area completely
    
    # Calculate new dimensions after scaling
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    # Resize image
    resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calculate crop box with bias toward keeping the top (head area)
    left = (new_width - target_width) // 2
    
    # For vertical cropping, prioritize keeping the top portion (head area)
    if new_height > target_height:
        # Keep more of the top portion - bias toward head area
        top = min(int((new_height - target_height) * 0.15), new_height - target_height)
    else:
        top = 0
    
    right = left + target_width
    bottom = top + target_height
    
    # Ensure crop box is within image bounds
    left = max(0, min(left, new_width - target_width))
    top = max(0, min(top, new_height - target_height))
    right = min(new_width, left + target_width)
    bottom = min(new_height, top + target_height)
    
    # Crop to exact target size
    return resized_img.crop((left, top, right, bottom))

def create_collage(image_paths, output_path, cell_size=300):
    """Create a collage from list of image paths"""
    if not image_paths:
        return
    
    num_images = len(image_paths)
    rows, cols = get_optimal_grid_size(num_images)
    
    # Create blank canvas
    canvas_width = cols * cell_size
    canvas_height = rows * cell_size
    collage = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # Place images in grid
    for i, img_path in enumerate(image_paths):
        try:
            # Open and resize image to fill cell completely
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize and crop to fill entire cell
            processed_img = resize_and_crop_to_fill(img, cell_size, cell_size)
            
            # Calculate position
            row = i // cols
            col = i % cols
            
            # Paste image onto canvas (no offset needed as it fills entire cell)
            x = col * cell_size
            y = row * cell_size
            collage.paste(processed_img, (x, y))
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue
    
    # Save collage
    collage.save(output_path, 'JPEG', quality=95)
    print(f"Created collage: {output_path}")

def main():
    base_dir = "/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/images/transfers"
    output_dir = "/Users/eugine_kang/Documents/hobby/Unnecessary Analysis/transfer_spending/images/collage"
    
    # Get all team folders
    team_folders = [f for f in os.listdir(base_dir) 
                   if os.path.isdir(os.path.join(base_dir, f))]
    
    for team_folder in team_folders:
        team_path = os.path.join(base_dir, team_folder)
        
        # Get all image files in the folder
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        image_paths = []
        
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(team_path, ext)))
        
        if image_paths:
            # Create output filename
            output_filename = f"{team_folder}.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"Processing {team_folder}: {len(image_paths)} images")
            create_collage(image_paths, output_path)
        else:
            print(f"No images found in {team_folder}")

if __name__ == "__main__":
    main()