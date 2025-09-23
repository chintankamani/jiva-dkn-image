#!/bin/bash

# Table Cropper Runner Script
# Usage: ./run_cropper.sh <image_filename>

# Check if image filename is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_cropper.sh <image_filename>"
    echo ""
    echo "Example:"
    echo "  ./run_cropper.sh my_table.png"
    echo ""
    echo "📁 Place your image file in the 'input' folder first!"
    echo "📁 Results will be saved in the 'output' folder"
    exit 1
fi

# Get the image filename
IMAGE_FILE="$1"

# Check if input folder exists
if [ ! -d "input" ]; then
    echo "❌ Error: 'input' folder not found."
    echo "Creating input and output folders..."
    mkdir -p input output
    echo "✅ Folders created. Please place your image in the 'input' folder and try again."
    exit 1
fi

# Check if the image file exists in input folder
if [ ! -f "input/$IMAGE_FILE" ]; then
    echo "❌ Error: Image file '$IMAGE_FILE' not found in 'input' folder."
    echo ""
    echo "📁 Available files in input folder:"
    ls -la input/*.png input/*.jpg input/*.jpeg input/*.bmp input/*.tiff 2>/dev/null || echo "   No image files found"
    echo ""
    echo "💡 Copy your image to the input folder:"
    echo "   cp /path/to/your/image.png input/"
    exit 1
fi

echo "🔄 Processing table image: $IMAGE_FILE"
echo "📁 Input folder: $(pwd)/input"
echo "📁 Output folder: $(pwd)/output"
echo ""

# Create output folder if it doesn't exist
mkdir -p output

# Activate virtual environment and run the script
source venv/bin/activate && python3 table_cropper.py "$IMAGE_FILE"

# Check if processing was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Success! Check these output files in the 'output' folder:"
    echo "   📄 ${IMAGE_FILE%.*}_cropped_table.png - Table without first column"
    echo "   📄 ${IMAGE_FILE%.*}_part1.png - Rows 1-8"
    echo "   📄 ${IMAGE_FILE%.*}_part2.png - Rows 9-17"
    echo ""
    echo "📂 All files saved in: $(pwd)/output"
else
    echo ""
    echo "❌ Error: Processing failed. Check the error messages above."
fi
