from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import shutil
import tempfile
from io import BytesIO
from PIL import Image
import zipfile
import requests

# Ensure project root is on path to import table_cropper
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from table_cropper import AdvancedTableCropper  # noqa: E402


app = FastAPI(title="DKN Table Cropper API (FastAPI)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "DKN Table Cropper API (FastAPI)", "version": "1.0.0"}


def process_image_internal(image: UploadFile):
    """Internal function to process image and return results"""
    # Basic content-type validation
    if image.content_type is None or not any(
        image.content_type.lower().endswith(ext) for ext in ["jpeg", "jpg", "png", "bmp", "tiff"]
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload PNG/JPG/JPEG/BMP/TIFF.")

    # Create an isolated temp working directory
    with tempfile.TemporaryDirectory() as work_dir:
        # Preserve the original filename base for output naming
        original_name = os.path.basename(image.filename or "uploaded.png")
        if "." in original_name:
            base_name, ext = os.path.splitext(original_name)
        else:
            base_name, ext = original_name, ".png"

        input_path = os.path.join(work_dir, original_name)

        # Persist uploaded file to disk
        with open(input_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # Process with AdvancedTableCropper in-memory
        cropper = AdvancedTableCropper()
        result = cropper.process_image(input_path, output_dir=None, return_images=True)
        
        return result, base_name


def upload_to_tmpfiles(image_bytes: bytes, filename: str) -> str:
    """Upload image to tmpfiles.org and return the public URL"""
    try:
        files = {"file": (filename, image_bytes, "image/png")}
        response = requests.post("https://tmpfiles.org/api/v1/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                # Extract the public URL from the response
                file_url = data.get("data", {}).get("url", "")
                if file_url:
                    # Ensure the URL has /dl/ and uses https
                    # Convert http to https and ensure /dl/ is present
                    if file_url.startswith("http://"):
                        file_url = file_url.replace("http://", "https://")
                    
                    # If the URL doesn't have /dl/, add it
                    if "/dl/" not in file_url:
                        file_url = file_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                    
                    return file_url
        
        raise Exception(f"Upload failed: {response.text}")
    except Exception as e:
        raise Exception(f"Failed to upload to tmpfiles.org: {str(e)}")


@app.post("/api/process/part1")
async def process_part1(image: UploadFile = File(...)):
    """Process image and return part 1 (rows 1-8) uploaded to tmpfiles.org"""
    try:
        result, base_name = process_image_internal(image)
        
        # Convert part1 to bytes
        img_buffer = BytesIO()
        save_img = result["part1"]
        if save_img.mode not in ("RGB", "RGBA"):
            save_img = save_img.convert("RGB")
        save_img.save(img_buffer, format="PNG")
        
        # Upload to tmpfiles.org
        filename = f"{base_name}_part1_rows1-8.png"
        image_bytes = img_buffer.getvalue()
        public_url = upload_to_tmpfiles(image_bytes, filename)
        
        return JSONResponse(content={
            "status": "success",
            "part": "part1",
            "description": "Rows 1-8",
            "filename": filename,
            "url": public_url,
            "size_bytes": len(image_bytes)
        })
        
    except HTTPException:
        raise
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"Processing failed: {str(exc)}"})


@app.post("/api/process/part2")
async def process_part2(image: UploadFile = File(...)):
    """Process image and return part 2 (rows 9-17) uploaded to tmpfiles.org"""
    try:
        result, base_name = process_image_internal(image)
        
        # Convert part2 to bytes
        img_buffer = BytesIO()
        save_img = result["part2"]
        if save_img.mode not in ("RGB", "RGBA"):
            save_img = save_img.convert("RGB")
        save_img.save(img_buffer, format="PNG")
        
        # Upload to tmpfiles.org
        filename = f"{base_name}_part2_rows9-17.png"
        image_bytes = img_buffer.getvalue()
        public_url = upload_to_tmpfiles(image_bytes, filename)
        
        return JSONResponse(content={
            "status": "success",
            "part": "part2",
            "description": "Rows 9-17",
            "filename": filename,
            "url": public_url,
            "size_bytes": len(image_bytes)
        })
        
    except HTTPException:
        raise
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"Processing failed: {str(exc)}"})


@app.post("/api/process/both")
async def process_both_parts(image: UploadFile = File(...)):
    """Process image and return both part1 and part2 uploaded to tmpfiles.org"""
    try:
        result, base_name = process_image_internal(image)
        
        # Process part1
        img_buffer1 = BytesIO()
        save_img1 = result["part1"]
        if save_img1.mode not in ("RGB", "RGBA"):
            save_img1 = save_img1.convert("RGB")
        save_img1.save(img_buffer1, format="PNG")
        
        # Process part2
        img_buffer2 = BytesIO()
        save_img2 = result["part2"]
        if save_img2.mode not in ("RGB", "RGBA"):
            save_img2 = save_img2.convert("RGB")
        save_img2.save(img_buffer2, format="PNG")
        
        # Upload both to tmpfiles.org
        filename1 = f"{base_name}_part1_rows1-8.png"
        filename2 = f"{base_name}_part2_rows9-17.png"
        
        url1 = upload_to_tmpfiles(img_buffer1.getvalue(), filename1)
        url2 = upload_to_tmpfiles(img_buffer2.getvalue(), filename2)
        
        return JSONResponse(content={
            "status": "success",
            "part1": {
                "description": "Rows 1-8",
                "filename": filename1,
                "url": url1,
                "size_bytes": len(img_buffer1.getvalue())
            },
            "part2": {
                "description": "Rows 9-17", 
                "filename": filename2,
                "url": url2,
                "size_bytes": len(img_buffer2.getvalue())
            }
        })
        
    except HTTPException:
        raise
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"Processing failed: {str(exc)}"})


@app.post("/api/process")
async def process(image: UploadFile = File(...)):
    """Process image and return ZIP with all results (original behavior)"""
    try:
        result, base_name = process_image_internal(image)

        # Package all images into a single zip in-memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
            def add_image_to_zip(pil_img: Image.Image, filename: str) -> None:
                buf = BytesIO()
                save_img = pil_img
                if pil_img.mode not in ("RGB", "RGBA"):
                    save_img = pil_img.convert("RGB")
                save_img.save(buf, format="PNG")
                zipf.writestr(filename, buf.getvalue())

            add_image_to_zip(result["cropped_table"], f"{base_name}_cropped_table.png")
            add_image_to_zip(result["part1"], f"{base_name}_part1_rows1-8.png")
            add_image_to_zip(result["part2"], f"{base_name}_part2_rows9-17.png")

            # Include metadata JSON
            meta_buf = BytesIO()
            import json as _json
            meta_buf.write(_json.dumps(result.get("metadata", {}), indent=2).encode("utf-8"))
            zipf.writestr(f"{base_name}_metadata.json", meta_buf.getvalue())

        headers = {
            "Content-Disposition": f"attachment; filename=\"{base_name}_processed.zip\""
        }
        return Response(content=zip_buffer.getvalue(), media_type="application/zip", headers=headers)

    except HTTPException:
        raise
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": f"Processing failed: {str(exc)}"})