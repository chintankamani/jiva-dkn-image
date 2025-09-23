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

# Ensure project root is on path to import table_cropper
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

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


@app.post("/api/process")
async def process(image: UploadFile = File(...)):
    try:
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