import base64
import io
import cv2
import numpy as np
from typing import List

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import our logic from core.py
from . import core

app = FastAPI()

# 1. Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 2. Setup Templates
templates = Jinja2Templates(directory="app/templates")

# --- Data Models ---

class Box(BaseModel):
    id: int
    x: int
    y: int
    w: int
    h: int

class ProcessRequest(BaseModel):
    image_base64: str
    boxes: List[Box]

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
def upload_image(file: UploadFile = File(...)):
    """
    Receives uploaded image with integrity checks.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    try:
        # Read file content
        content = file.file.read()
        file_size_kb = len(content) / 1024
        
        # --- DATA INTEGRITY CHECK ---
        # We decode it here just to verify the upload is healthy
        nparr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            print("[ERROR] Uploaded bytes could not be decoded into an image.")
            raise ValueError("Invalid image encoding.")
            
        h, w, c = img.shape
        print(f"[DEBUG] Received Image: {w}x{h} | Size: {file_size_kb:.2f} KB")
        # -----------------------------

        # Process with OCR
        result = core.detect_text_regions(content)
        return result
        
    except Exception as e:
        print(f"[ERROR] Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process")
def process_image(request: ProcessRequest):
    """
    Applies blur to selected regions.
    """
    try:
        # Decode the Base64 image
        if "," in request.image_base64:
            _, encoded = request.image_base64.split(",", 1)
        else:
            encoded = request.image_base64
            
        image_bytes = base64.b64decode(encoded)

        # Convert Pydantic models to dicts
        # (Compatible with Pydantic v1 and v2)
        boxes_dict = []
        for box in request.boxes:
            boxes_dict.append(box.dict() if hasattr(box, 'dict') else box.model_dump())
        
        # Apply Blur
        final_image_bytes = core.apply_blur(image_bytes, boxes_dict)

        if final_image_bytes is None:
            raise ValueError("Blur application returned empty result.")

        return StreamingResponse(
            io.BytesIO(final_image_bytes), 
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=blurred_result.jpg"}
        )

    except Exception as e:
        print(f"[ERROR] Blur processing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image.")