# 🔗 DKN Table Cropper API Documentation

Backend API service for automated table image processing. Designed for integration with Next.js frontend applications.

## 🚀 **API Endpoints**

### **Health Check**
```
GET /api/health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "DKN Table Cropper API",
  "version": "1.0.0"
}
```

### **API Information**
```
GET /api/info
```
**Response:**
```json
{
  "service": "DKN Table Cropper API",
  "version": "1.0.0",
  "description": "Advanced table image processor with perspective correction",
  "features": [...],
  "supported_formats": ["PNG", "JPG", "JPEG", "BMP", "TIFF"],
  "max_file_size": "16MB",
  "endpoints": {...}
}
```

## 📷 **Image Processing**

### **Main Processing Endpoint**
```
POST /api/process
Content-Type: application/json OR multipart/form-data
```

**Supports two input formats:**

#### **1. Base64 JSON (Recommended for Next.js)**
```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA..."
}
```

#### **2. File Upload (FormData)**
```javascript
const formData = new FormData();
formData.append('image', file);
```

**Response:**
```json
{
  "success": true,
  "results": {
    "corners": "data:image/png;base64,iVBORw...",
    "perspective_corrected": "data:image/png;base64,iVBORw...",
    "cropped_table": "data:image/png;base64,iVBORw...",
    "left_cropped": "data:image/png;base64,iVBORw...",
    "part1_rows1_8": "data:image/png;base64,iVBORw...",
    "part2_rows9_17": "data:image/png;base64,iVBORw..."
  },
  "metadata": {
    "original_dimensions": "1280 x 955",
    "corrected_dimensions": "1364 x 850",
    "detected_corners": [[72, 302], [1183, 268], [1224, 931], [36, 945]],
    "cell_dimensions": "42 x 50"
  },
  "processing_info": {
    "files_generated": 6,
    "original_filename": "table.png",
    "processing_timestamp": "1640995200"
  }
}
```

### **Legacy File Upload Endpoint**
```
POST /api/process-file
Content-Type: multipart/form-data
```
Same as `/api/process` but only supports file uploads.

## 🎯 **Next.js Integration Examples**

### **React Hook for Image Processing**
```typescript
// hooks/useTableCropper.ts
import { useState } from 'react';

interface ProcessingResult {
  success: boolean;
  results?: {
    corners: string;
    perspective_corrected: string;
    cropped_table: string;
    left_cropped: string;
    part1_rows1_8: string;
    part2_rows9_17: string;
  };
  metadata?: any;
  error?: string;
}

export const useTableCropper = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);

  const processImage = async (imageFile: File): Promise<ProcessingResult> => {
    setLoading(true);
    try {
      // Convert file to base64
      const base64 = await fileToBase64(imageFile);
      
      const response = await fetch('/api/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64
        })
      });

      const data = await response.json();
      setResult(data);
      return data;
    } catch (error) {
      const errorResult = { success: false, error: error.message };
      setResult(errorResult);
      return errorResult;
    } finally {
      setLoading(false);
    }
  };

  return { processImage, loading, result };
};

// Utility function
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = error => reject(error);
  });
};
```

### **API Route Handler (Next.js 13+)**
```typescript
// app/api/crop-table/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { image } = await request.json();
    
    // Forward to Flask backend
    const response = await fetch(`${process.env.FLASK_API_URL}/api/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image })
    });

    const data = await response.json();
    
    if (!data.success) {
      return NextResponse.json({ error: data.error }, { status: 400 });
    }

    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Processing failed' }, 
      { status: 500 }
    );
  }
}
```

### **Component Example**
```tsx
// components/TableCropper.tsx
'use client';

import { useState } from 'react';
import { useTableCropper } from '@/hooks/useTableCropper';

export default function TableCropper() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { processImage, loading, result } = useTableCropper();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleProcess = async () => {
    if (!selectedFile) return;
    
    const result = await processImage(selectedFile);
    
    if (result.success) {
      // Handle successful processing
      console.log('Processing completed:', result.results);
      // Save results to state/database
      // Display processed images
    } else {
      // Handle error
      console.error('Processing failed:', result.error);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">DKN Table Cropper</h2>
      
      <div className="space-y-4">
        <input
          type="file"
          accept="image/*"
          onChange={handleFileSelect}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        
        <button
          onClick={handleProcess}
          disabled={!selectedFile || loading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          {loading ? 'Processing...' : 'Process Table'}
        </button>
        
        {result && (
          <div className="mt-6">
            {result.success ? (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-green-600">✅ Processing Completed</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(result.results).map(([key, base64]) => (
                    <div key={key} className="border rounded p-2">
                      <h4 className="text-sm font-medium mb-2">{key.replace('_', ' ')}</h4>
                      <img 
                        src={base64} 
                        alt={key}
                        className="w-full h-auto border"
                      />
                      <a
                        href={base64}
                        download={`${key}.png`}
                        className="inline-block mt-2 px-3 py-1 bg-gray-200 text-sm rounded hover:bg-gray-300"
                      >
                        Download
                      </a>
                    </div>
                  ))}
                </div>
                
                <div className="mt-4 p-3 bg-gray-50 rounded">
                  <h4 className="font-medium">Processing Details:</h4>
                  <pre className="text-xs mt-2">
                    {JSON.stringify(result.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="text-red-600">
                ❌ Error: {result.error}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

## 🔧 **Environment Setup**

### **Environment Variables**
```env
# .env.local (Next.js)
FLASK_API_URL=https://your-flask-api.vercel.app

# Or for local development
FLASK_API_URL=http://localhost:5000
```

### **CORS Configuration**
The Flask API includes CORS headers to allow requests from Next.js frontends:
```python
from flask_cors import CORS
CORS(app)  # Allows all origins
```

## 📊 **Processing Features**

### **Automatic Processing Pipeline**
1. **📍 Corner Detection**: Automatic table boundary detection
2. **🎯 Right Corner Adjustment**: +30px to capture 31st column fully
3. **🔧 Perspective Correction**: Lanczos interpolation (1364×850)
4. **✂️ Column Removal**: Intelligent first column removal
5. **⬅️ Left Crop**: 26% removal for optimal data extraction
6. **📊 Equal Split**: Rows 1-8 and rows 9-17

### **Output Files**
- `corners`: Corner detection visualization
- `perspective_corrected`: Straightened table
- `cropped_table`: Table without first column
- `left_cropped`: 26% left-cropped for splitting
- `part1_rows1_8`: First 8 rows
- `part2_rows9_17`: Last 9 rows

## 🚀 **Deployment**

### **Vercel Deployment**
```bash
# Deploy Flask backend
vercel --prod

# Get API URL
# https://your-app.vercel.app
```

### **Next.js Integration**
```bash
# Install dependencies
npm install

# Set environment variables
echo "FLASK_API_URL=https://your-flask-api.vercel.app" > .env.local

# Deploy Next.js frontend
vercel --prod
```

## 🔍 **Error Handling**

### **Common Error Responses**
```json
// Invalid file type
{
  "error": "Invalid file type. Please upload PNG, JPG, JPEG, BMP, or TIFF"
}

// Processing failure
{
  "error": "Processing failed: [detailed error message]"
}

// Missing image data
{
  "error": "No image data provided in JSON"
}
```

### **Status Codes**
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error (processing failure)

## 🎯 **Best Practices**

### **For Next.js Integration**
1. **Use Base64 format** for JSON requests (easier than FormData)
2. **Implement error boundaries** for robust error handling  
3. **Add loading states** for better UX during processing
4. **Cache results** to avoid reprocessing same images
5. **Validate file types** on frontend before sending

### **Performance Optimization**
1. **Compress images** before sending (< 2MB recommended)
2. **Use Web Workers** for base64 conversion in frontend
3. **Implement request timeouts** (processing takes 2-5 seconds)
4. **Add retry logic** for network failures

This API is ready for production use with your Next.js application! 🚀
