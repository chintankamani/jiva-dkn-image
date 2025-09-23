from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import tempfile
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import json
import base64

# Add the parent directory to the path so we can import our cropper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from table_cropper_advanced import AdvancedTableCropper

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'DKN Table Cropper API',
        'version': '1.0.0'
    })

@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'service': 'DKN Table Cropper API',
        'version': '1.0.0',
        'description': 'Advanced table image processor with perspective correction',
        'features': [
            'Automatic corner detection',
            'Perspective correction with Lanczos interpolation',
            'Right corner adjustment (+30px) for 31st column capture',
            'Accurate first column removal',
            '26% left crop before splitting',
            'Equal row splitting (8 + 9 rows)',
            'Detailed processing metadata'
        ],
        'supported_formats': ['PNG', 'JPG', 'JPEG', 'BMP', 'TIFF'],
        'max_file_size': '16MB',
        'endpoints': {
            'POST /api/process': 'Process table image and return base64 encoded results',
            'POST /api/process-file': 'Process image file upload',
            'GET /api/health': 'Health check',
            'GET /api/info': 'API information'
        }
    })

@app.route('/api/process', methods=['POST'])
def process_image():
    """
    Process table image from base64 or file upload.
    Designed for automated processing from Next.js frontend.
    
    Request formats:
    1. JSON with base64: {"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."}
    2. Form data with file: multipart/form-data with 'image' field
    
    Response: JSON with base64 encoded results
    """
    try:
        # Handle base64 image from JSON request
        if request.is_json:
            data = request.get_json()
            if 'image' not in data:
                return jsonify({'error': 'No image data provided in JSON'}), 400
            
            image_data = data['image']
            
            # Parse base64 image
            if image_data.startswith('data:'):
                # Remove data URL prefix
                header, encoded = image_data.split(',', 1)
                image_bytes = base64.b64decode(encoded)
            else:
                # Assume it's raw base64
                image_bytes = base64.b64decode(image_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(image_bytes)
                input_path = temp_file.name
            
            filename = 'uploaded_image.png'
        
        # Handle file upload
        elif 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, BMP, or TIFF'}), 400
            
            filename = secure_filename(file.filename)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{filename.split(".")[-1]}', delete=False) as temp_file:
                file.save(temp_file.name)
                input_path = temp_file.name
        
        else:
            return jsonify({'error': 'No image provided'}), 400
        
        try:
            # Create output directory
            with tempfile.TemporaryDirectory() as output_dir:
                # Process the image
                cropper = AdvancedTableCropper()
                success = cropper.process_image(input_path, output_dir)
                
                if not success:
                    return jsonify({'error': 'Failed to process image'}), 500
                
                # Read all output files and convert to base64
                base_filename = os.path.splitext(filename)[0]
                results = {}
                
                file_mappings = {
                    'corners': f"{base_filename}_corners.png",
                    'perspective_corrected': f"{base_filename}_perspective_corrected.png", 
                    'cropped_table': f"{base_filename}_cropped_table.png",
                    'left_cropped': f"{base_filename}_left_cropped.png",
                    'part1_rows1_8': f"{base_filename}_part1_rows1-8.png",
                    'part2_rows9_17': f"{base_filename}_part2_rows9-17.png"
                }
                
                # Convert images to base64
                for key, file_name in file_mappings.items():
                    file_path = os.path.join(output_dir, file_name)
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            image_data = f.read()
                            encoded = base64.b64encode(image_data).decode('utf-8')
                            results[key] = f"data:image/png;base64,{encoded}"
                
                # Read metadata
                metadata_path = os.path.join(output_dir, f"{base_filename}_metadata.json")
                metadata = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                
                # Clean up temp input file
                if os.path.exists(input_path):
                    os.unlink(input_path)
                
                return jsonify({
                    'success': True,
                    'results': results,
                    'metadata': metadata,
                    'processing_info': {
                        'files_generated': len(results),
                        'original_filename': filename,
                        'processing_timestamp': str(int(__import__('time').time()))
                    }
                })
        
        finally:
            # Ensure temp file is cleaned up
            if os.path.exists(input_path):
                os.unlink(input_path)
    
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/process-file', methods=['POST'])  
def process_file_upload():
    """
    Legacy endpoint for file uploads only.
    Use /api/process for automated processing.
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PNG, JPG, JPEG, BMP, or TIFF'}), 400
        
        # Forward to main process endpoint
        return process_image()
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
