#!/usr/bin/env python3
"""
Script to download the first image from a web search using bing-image-downloader.
Searches Bing Images for the provided query and downloads the first result.

Usage:
    python download_web_image.py "query here"
    python download_web_image.py "09/10 Real Madrid Christiano Ronaldo"
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
import re
from bing_image_downloader import downloader


def sanitize_filename(query):
    """
    Convert a search query into a safe filename.
    
    Args:
        query (str): The search query
        
    Returns:
        str: Sanitized filename
    """
    # Convert to lowercase
    filename = query.lower()
    
    # Replace problematic characters
    filename = re.sub(r'[/\\]', '-', filename)  # Replace slashes with hyphens
    filename = re.sub(r'[<>:"|?*]', '', filename)  # Remove other problematic chars
    filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
    filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores with single
    filename = filename.strip('_-')  # Remove leading/trailing underscores and hyphens
    
    # Ensure it's not too long
    if len(filename) > 100:
        filename = filename[:100].rstrip('_-')
    
    return filename


def download_first_image(query, output_dir="../images/", custom_filename=None):
    """
    Download the first image from Bing search results.
    
    Args:
        query (str): Search query
        output_dir (str): Directory to save the image
        custom_filename (str): Optional custom filename
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate filename from query if not provided
    if custom_filename is None:
        safe_filename = sanitize_filename(query)
        final_filename = f"{safe_filename}.jpg"
    else:
        final_filename = custom_filename
        if not final_filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            final_filename += '.jpg'
    
    print(f"Searching for: {query}")
    print(f"Will save as: {final_filename}")
    print(f"Output directory: {output_path}")
    
    # Create a temporary directory for bing-image-downloader
    temp_download_dir = Path("./temp_downloads").resolve()
    temp_download_dir.mkdir(exist_ok=True)
    
    try:
        # Use bing-image-downloader to search and download
        print("Searching Bing Images...")
        
        # Change to temp directory to control where downloads go
        original_cwd = os.getcwd()
        os.chdir(temp_download_dir)
        
        # Download images (limit to 1 to get just the first image)
        downloader.download(query, limit=1, output_dir='.', 
                          adult_filter_off=True, force_replace=False, timeout=30)
        
        # Change back to original directory
        os.chdir(original_cwd)
        
        # bing-image-downloader creates: temp_downloads/query/query/image.jpg
        # But we need to handle the exact folder name it creates
        print("Looking for downloaded images...")
        
        # Find the folder that was actually created (it uses the exact query as folder name)
        query_base_folder = None
        for item in temp_download_dir.iterdir():
            if item.is_dir() and item.name.strip().lower() == query.strip().lower():
                query_base_folder = item
                break
        
        if not query_base_folder:
            # If exact match not found, try to find any folder (in case of encoding issues)
            folders = [item for item in temp_download_dir.iterdir() if item.is_dir()]
            if folders:
                query_base_folder = folders[0]  # Use the first/only folder created
                print(f"Using folder: {query_base_folder.name}")
        
        if not query_base_folder:
            print(f"No download folder found in: {temp_download_dir}")
            print("Available items:", list(temp_download_dir.iterdir()))
            return False
        
        # Look for the nested folder inside (bing-image-downloader creates nested structure)
        query_images_folder = None
        for item in query_base_folder.iterdir():
            if item.is_dir():
                query_images_folder = item
                break
        
        if not query_images_folder:
            # Sometimes images are directly in the base folder
            query_images_folder = query_base_folder
        
        print(f"Searching for images in: {query_images_folder}")
        
        # Find image files
        image_files = []
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        
        for file_path in query_images_folder.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
                image_files.append(file_path)
        
        if not image_files:
            print("No image files found in download folder")
            print("Folder contents:", list(query_images_folder.iterdir()))
            return False
        
        # Get the first image
        first_image = image_files[0]
        print(f"Found image: {first_image}")
        
        # Copy to target location with desired filename
        target_path = output_path / final_filename
        shutil.copy2(first_image, target_path)
        
        print(f"Image saved to: {target_path}")
        print(f"File size: {target_path.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error downloading image: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
        
    finally:
        # Clean up temporary directory
        if temp_download_dir.exists():
            try:
                shutil.rmtree(temp_download_dir)
                print("Cleaned up temporary files")
            except Exception as e:
                print(f"Warning: Could not clean up temp directory: {e}")


def main():
    """Main function to run the image search and download."""
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Download the first image from a Bing Images search query',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python download_web_image.py "Cristiano Ronaldo"
    python download_web_image.py "09/10 Real Madrid Christiano Ronaldo"
    python download_web_image.py "Lionel Messi Barcelona"
        '''
    )
    
    parser.add_argument(
        'query',
        help='Search query for the image'
    )
    
    parser.add_argument(
        '--output-dir',
        default='../images/',
        help='Output directory for downloaded images (default: ../images/)'
    )
    
    parser.add_argument(
        '--filename',
        help='Custom filename for the downloaded image (optional)'
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        # No arguments provided, show help
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Bing Image Search and Download Script")
    print("=" * 60)
    print(f"Query: {args.query}")
    
    if args.filename:
        print(f"Custom filename: {args.filename}")
        custom_filename = args.filename
    else:
        safe_filename = sanitize_filename(args.query)
        custom_filename = f"{safe_filename}.jpg"
        print(f"Generated filename: {custom_filename}")
    
    print(f"Output directory: {args.output_dir}")
    print("=" * 60)
    
    # Try to download the image
    success = download_first_image(
        query=args.query,
        output_dir=args.output_dir,
        custom_filename=custom_filename
    )
    
    if success:
        print("\n✓ Image downloaded successfully!")
        print(f"Saved as: {custom_filename}")
    else:
        print("\n✗ Failed to download image")
        print("Please check your internet connection or try a different query.")


if __name__ == "__main__":
    main()