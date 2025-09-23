#!/bin/bash

# Advanced Table Cropper Runner Script with Perspective Correction
# Usage: ./run_advanced_cropper.sh <image_filename>

# Check if image filename is provided
if [ $# -eq 0 ]; then
    echo "🚀 Advanced Table Cropper with Perspective Correction"
    echo ""
    echo "Usage: ./run_advanced_cropper.sh <image_filename>"
    echo ""
    echo "Example:"
    echo "  ./run_advanced_cropper.sh my_table.png"
    echo ""
    echo "✨ Features:"
    echo "  📍 Automatic corner detection"
    echo "  🔧 Perspective correction with Lanczos interpolation"
    echo "  🎯 Right corners moved 30px right + 10% margin (captures 31st column)"
    echo "  ✂️  Accurate first column removal"
    echo "  ⬅️  26% left crop before splitting"
    echo "  📊 Equal row splitting (8 + 9 rows)"
    echo "  📋 Detailed processing metadata"
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

echo "🚀 Processing table image with advanced algorithms: $IMAGE_FILE"
echo "📁 Input folder: $(pwd)/input"
echo "📁 Output folder: $(pwd)/output"
echo ""
echo "⚡ Starting advanced processing..."
echo "   📍 Detecting table corners..."
echo "   🎯 Adjusting right corners (+30px to capture 31st column)..."
echo "   🔧 Applying perspective correction (10% margin AFTER 31st column)..."
echo "   ✂️  Removing first column..."
echo "   ⬅️  Cropping 26% from left..."
echo "   📊 Splitting into equal parts..."
echo ""

# Create output folder if it doesn't exist
mkdir -p output

# Activate virtual environment and run the advanced script
source venv/bin/activate && python3 table_cropper_advanced.py "$IMAGE_FILE"

# Check if processing was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Advanced processing completed!"
    echo ""
    echo "📂 Generated files in 'output' folder:"
    echo "   🔍 ${IMAGE_FILE%.*}_corners.png - Corner detection visualization"
    echo "   🔧 ${IMAGE_FILE%.*}_perspective_corrected.png - All 31 columns + 10% margin"
    echo "   ✂️  ${IMAGE_FILE%.*}_cropped_table.png - Table without first column"
    echo "   ⬅️  ${IMAGE_FILE%.*}_left_cropped.png - 26% left-cropped table"
    echo "   📄 ${IMAGE_FILE%.*}_part1_rows1-8.png - First 8 rows"
    echo "   📄 ${IMAGE_FILE%.*}_part2_rows9-17.png - Last 9 rows"
    echo "   📋 ${IMAGE_FILE%.*}_metadata.json - Processing details"
    echo ""
    echo "🎯 The advanced algorithm provides:"
    echo "   ✅ Right corners adjusted (+30px) to capture 31st column"
    echo "   ✅ Automatic perspective correction with margin AFTER 31st column"
    echo "   ✅ All 31 columns fully preserved and visible"
    echo "   ✅ Accurate column boundary detection"
    echo "   ✅ 26% left crop before splitting"
    echo "   ✅ Equal row distribution"
    echo "   ✅ High-quality Lanczos interpolation"
    echo ""
    echo "📂 All files saved in: $(pwd)/output"
else
    echo ""
    echo "❌ Error: Advanced processing failed. Check the error messages above."
    echo ""
    echo "💡 Try the basic version if needed:"
    echo "   ./run_cropper.sh $IMAGE_FILE"
fi
