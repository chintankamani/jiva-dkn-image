# Table Cropper - How to Run and Use

## Quick Start Command

```bash
# Activate virtual environment and run the script
source venv/bin/activate && python3 table_cropper.py your_table_image.png
```

## Folder Structure

```
table cropper/
├── input/          ← Place your images here
├── output/         ← Results will be saved here
├── table_cropper.py
├── run_cropper.sh  ← Easy-to-use script
└── requirements.txt
```

## Step-by-Step Instructions

### 1. Prepare Your Table Image

- Place your table image file in the `input/` folder
- Supported formats: PNG, JPG, JPEG, BMP, TIFF
- The image should contain a table with 32 columns and 17 rows
- Example: Copy `my_table.png` to `input/my_table.png`

### 2. Run the Script

**Option A: Easy way (recommended)**
```bash
./run_cropper.sh my_table.png
```

**Option B: Manual way**
```bash
# Navigate to the project directory
cd "/Users/arjun/Desktop/table cropper"

# Activate the virtual environment
source venv/bin/activate

# Run the script with your image filename (not full path)
python3 table_cropper.py my_table.png
```

### 3. Check Results

After running the script, you'll find three new files in the `output/` folder:

1. **`my_table_cropped_table.png`** - Original table with first column (labels) removed
2. **`my_table_part1.png`** - Rows 1-8 (first part)
3. **`my_table_part2.png`** - Rows 9-17 (second part)

## Example Usage

```bash
# Step 1: Copy your image to input folder
cp ~/Desktop/sales_data.png input/

# Step 2: Run the script (easy way)
./run_cropper.sh sales_data.png

# Or run manually
source venv/bin/activate && python3 table_cropper.py sales_data.png
```

## What the Script Does

1. **Loads** your table image
2. **Calculates** cell dimensions automatically based on 32 columns × 17 rows
3. **Removes** the first column (typically labels/headers)
4. **Keeps** columns 1-31 (usually data columns)
5. **Splits** the result into two parts:
   - Part 1: Rows 1-8
   - Part 2: Rows 9-17
6. **Saves** all three outputs in the same directory

## Troubleshooting

### Common Issues:

**"No module named 'PIL'"**
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**"Image file not found"**
- Check that your image file exists in the correct location
- Use the full path if the image is elsewhere
- Verify the filename and extension

**"Error processing image"**
- Ensure your image is a valid image file
- Check that the image isn't corrupted
- Try with a different image format

### File Locations

- **Script location**: `/Users/arjun/Desktop/table cropper/table_cropper.py`
- **Input images**: Place in `/Users/arjun/Desktop/table cropper/input/`
- **Output files**: Saved in `/Users/arjun/Desktop/table cropper/output/`

## Testing the Script

To test if everything works:

1. Find any table image (or create a test image)
2. Copy it to the `input/` folder: `cp test_image.png input/`
3. Run: `./run_cropper.sh test_image.png`
4. Check the `output/` folder for the three result files

The script will display progress messages showing:
- Input/output folder locations
- Image dimensions
- Calculated cell dimensions
- Files being saved
- Final output file locations
