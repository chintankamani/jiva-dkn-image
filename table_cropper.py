#!/usr/bin/env python3
"""
Table Image Cropper and Splitter

This script processes a table image with 32 columns and 17 rows:
- Removes the first column (labels) and keeps columns 1-31
- Splits the result into two parts: rows 1-8 and rows 9-17
- Uses dynamic sizing based on image dimensions
- Automatically reads from 'input' folder and saves to 'output' folder

Usage: python table_cropper.py <image_filename>
"""

import sys
from PIL import Image
import os


def calculate_cell_dimensions(image_width, image_height, total_cols=32, total_rows=17):
    """
    Calculate cell dimensions based on image size.
    
    Args:
        image_width (int): Width of the input image
        image_height (int): Height of the input image
        total_cols (int): Total number of columns in the table
        total_rows (int): Total number of rows in the table
    
    Returns:
        tuple: (cell_width, cell_height)
    """
    cell_width = image_width // total_cols
    cell_height = image_height // total_rows
    return cell_width, cell_height


def crop_remove_first_column(image, cell_width, total_cols=32):
    """
    Remove the first column (labels) and keep columns 1-31.
    
    Args:
        image (PIL.Image): Input image
        cell_width (int): Width of each cell
        total_cols (int): Total number of columns
    
    Returns:
        PIL.Image: Cropped image without the first column
    """
    # Calculate crop coordinates to remove first column
    left = cell_width  # Start from the second column
    top = 0
    right = image.width  # Keep to the end
    bottom = image.height
    
    return image.crop((left, top, right, bottom))


def split_image_by_rows(image, cell_height, split_row=8):
    """
    Split the image into two parts at the specified row.
    
    Args:
        image (PIL.Image): Input image
        cell_height (int): Height of each cell
        split_row (int): Row number where to split (1-indexed)
    
    Returns:
        tuple: (part1_image, part2_image)
    """
    # Part 1: rows 1 to split_row
    part1 = image.crop((0, 0, image.width, split_row * cell_height))
    
    # Part 2: rows (split_row + 1) to end
    part2 = image.crop((0, split_row * cell_height, image.width, image.height))
    
    return part1, part2


def process_table_image(input_path, output_dir=None):
    """
    Main function to process the table image.
    
    Args:
        input_path (str): Path to the input image
        output_dir (str): Directory to save output images (defaults to 'output' folder)
    """
    try:
        # Load the image
        print(f"Loading image: {input_path}")
        image = Image.open(input_path)
        print(f"Image dimensions: {image.width} x {image.height}")
        
        # Set output directory to 'output' folder if not specified
        if output_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "output")
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Calculate cell dimensions
        cell_width, cell_height = calculate_cell_dimensions(image.width, image.height)
        print(f"Calculated cell dimensions: {cell_width} x {cell_height}")
        
        # Step 1: Remove first column (labels) and keep columns 1-31
        print("Removing first column (labels)...")
        cropped_image = crop_remove_first_column(image, cell_width)
        
        # Get base filename without extension for output naming
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        
        # Save the cropped table (31 columns × 17 rows)
        cropped_output_path = os.path.join(output_dir, f"{input_filename}_cropped_table.png")
        cropped_image.save(cropped_output_path)
        print(f"Saved cropped table: {cropped_output_path}")
        
        # Step 2: Split the cropped image into two parts
        print("Splitting image into two parts...")
        part1, part2 = split_image_by_rows(cropped_image, cell_height, split_row=8)
        
        # Save part 1 (rows 1-8)
        part1_output_path = os.path.join(output_dir, f"{input_filename}_part1.png")
        part1.save(part1_output_path)
        print(f"Saved part 1 (rows 1-8): {part1_output_path}")
        
        # Save part 2 (rows 9-17)
        part2_output_path = os.path.join(output_dir, f"{input_filename}_part2.png")
        part2.save(part2_output_path)
        print(f"Saved part 2 (rows 9-17): {part2_output_path}")
        
        print("\nProcessing completed successfully!")
        print(f"Output files:")
        print(f"  - {cropped_output_path}")
        print(f"  - {part1_output_path}")
        print(f"  - {part2_output_path}")
        
    except FileNotFoundError:
        print(f"Error: Image file not found: {input_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        sys.exit(1)


def main():
    """
    Main entry point for the script.
    """
    if len(sys.argv) != 2:
        print("Usage: python table_cropper.py <image_filename>")
        print("\nExample:")
        print("  python table_cropper.py my_table.png")
        print("\nNote: Place your image in the 'input' folder first!")
        print("\nThe script will:")
        print("  1. Look for the image in the 'input' folder")
        print("  2. Remove the first column (labels)")
        print("  3. Keep columns 1-31 (date columns)")
        print("  4. Split into two parts: rows 1-8 and rows 9-17")
        print("  5. Save results in the 'output' folder")
        sys.exit(1)
    
    image_filename = sys.argv[1]
    
    # Get script directory and construct input path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    input_image_path = os.path.join(input_dir, image_filename)
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: 'input' folder does not exist. Please create it first.")
        sys.exit(1)
    
    # Check if input file exists
    if not os.path.exists(input_image_path):
        print(f"Error: Image file not found: {input_image_path}")
        print(f"Available files in input folder:")
        try:
            files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
            if files:
                for f in files:
                    print(f"  - {f}")
            else:
                print("  No image files found in input folder")
        except:
            print("  Could not list files in input folder")
        sys.exit(1)
    
    # Process the image
    print(f"📁 Input folder: {input_dir}")
    print(f"📁 Output folder: {os.path.join(script_dir, 'output')}")
    print()
    process_table_image(input_image_path)


if __name__ == "__main__":
    main()
