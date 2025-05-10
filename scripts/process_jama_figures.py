#!/usr/bin/env python3
# Script to process figures according to JAMA requirements
import os
from PIL import Image
import sys

# Check if PIL is installed
try:
    from PIL import Image
except ImportError:
    print("Pillow package is required. Install it using: pip install Pillow")
    sys.exit(1)

# Create directories if they don't exist
figures_dir = '../JAMA_submission/figures'
os.makedirs(figures_dir, exist_ok=True)

# Source figures
source_figures = [
    '../figures/figure1_sex_distribution.png',
    '../figures/figure2_inclusion_rates.png',
    '../figures/figure3_disease_distribution.png'
]

# Target figures
target_figures = [
    os.path.join(figures_dir, 'figure1.tif'),
    os.path.join(figures_dir, 'figure2.tif'),
    os.path.join(figures_dir, 'figure3.tif')
]

# Required DPI for JAMA
required_dpi = 300

def process_figure(source_path, target_path):
    """Process a figure to meet JAMA requirements"""
    try:
        # Open the image
        img = Image.open(source_path)
        
        # Get the original size
        width, height = img.size
        print(f"Processing {source_path} - Original size: {width}x{height}")
        
        # Calculate appropriate dimensions for 300 DPI
        # Assuming original image is 72 DPI (standard screen resolution)
        original_dpi = 72  # Standard screen resolution
        
        # Calculate new dimensions to maintain equivalent size at 300 DPI
        new_width = width * required_dpi // original_dpi
        new_height = height * required_dpi // original_dpi
        
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to RGB if it's not already (TIFF supports various color modes)
        if resized_img.mode != 'RGB':
            resized_img = resized_img.convert('RGB')
        
        # Save as TIFF with high quality and 300 DPI
        resized_img.save(
            target_path,
            format='TIFF',
            dpi=(required_dpi, required_dpi),
            compression='lzw'  # LZW compression maintains quality
        )
        
        print(f"Saved {target_path} - New size: {new_width}x{new_height} at {required_dpi} DPI")
        return True
    
    except Exception as e:
        print(f"Error processing {source_path}: {e}")
        return False

def main():
    """Main function to process all figures"""
    print("Processing figures for JAMA submission...")
    
    success_count = 0
    for i, (source, target) in enumerate(zip(source_figures, target_figures)):
        print(f"\nProcessing Figure {i+1}:")
        if process_figure(source, target):
            success_count += 1
    
    print(f"\nProcessing complete. Successfully processed {success_count} of {len(source_figures)} figures.")

if __name__ == "__main__":
    main()

