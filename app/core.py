import os
import cv2
import numpy as np
import base64

# --- STABILITY INITIALIZATION ---
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["FLAGS_enable_mkldnn"] = "0"

from paddleocr import PaddleOCR

# Global OCR variable
ocr = None

def init_ocr():
    global ocr
    if ocr is None:
        try:
            print("[INFO] Initializing OCR (Safe Mode - 2.6.2)...")
            
            # We use the most basic initialization to prevent 
            # the 'set_optimization_level' attribute crash.
            ocr = PaddleOCR(
                use_angle_cls=False, 
                lang='en',
                show_log=False,
                # Force version 3 to avoid the v4 experimental LCNet models
                ocr_version='PP-OCRv3' 
            )
            print("[INFO] OCR Model Loaded Successfully.")
        except AttributeError as ae:
            print(f"[CRITICAL] Version Mismatch detected: {ae}")
            print("[INFO] Attempting Emergency Fallback...")
            # Fallback: remove all optional flags
            try:
                ocr = PaddleOCR(lang='en')
            except Exception as final_e:
                print(f"[FATAL] Fallback failed: {final_e}")
        except Exception as e:
            print(f"[ERROR] Failed to load OCR Model: {e}")
            ocr = None

# Initialize on file load
init_ocr()

def bytes_to_cv2(image_bytes: bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def cv2_to_base64(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')

def detect_text_regions(image_bytes: bytes):
    if ocr is None:
        init_ocr()
    
    img = bytes_to_cv2(image_bytes)
    if img is None:
        raise ValueError("Invalid image data.")

    h, w, _ = img.shape
    
    try:
        # Standard inference
        result = ocr.ocr(img)
    except Exception as e:
        print(f"[ERROR] Inference Failed: {e}")
        raise RuntimeError(f"OCR Error: {e}")

    boxes = []
    
    if result and result[0]:
        for i, line in enumerate(result[0]):
            box_coords = line[0]
            xs = [pt[0] for pt in box_coords]
            ys = [pt[1] for pt in box_coords]

            x_min, y_min = int(min(xs)), int(min(ys))
            x_max, y_max = int(max(xs)), int(max(ys))

            pad = 5
            x_min = max(0, x_min - pad)
            y_min = max(0, y_min - pad)
            x_max = min(w, x_max + pad)
            y_max = min(h, y_max + pad)

            boxes.append({
                "id": i,
                "x": x_min, "y": y_min, 
                "w": x_max - x_min, "h": y_max - y_min
            })

    return {
        "image_base64": cv2_to_base64(img),
        "width": w, "height": h, "boxes": boxes
    }

def apply_blur(image_bytes: bytes, boxes: list):
    img = bytes_to_cv2(image_bytes)
    if img is None: return None
    
    for box in boxes:
        x, y, w, h = int(box['x']), int(box['y']), int(box['w']), int(box['h'])
        h_img, w_img, _ = img.shape
        if w > 0 and h > 0:
            x, y = max(0, min(x, w_img - 1)), max(0, min(y, h_img - 1))
            w, h = min(w, w_img - x), min(h, h_img - y)

            roi = img[y:y+h, x:x+w]
            # Standard Gaussian Blur
            blurred_roi = cv2.GaussianBlur(roi, (51, 51), 30)
            img[y:y+h, x:x+w] = blurred_roi

    _, encoded_img = cv2.imencode('.jpg', img)
    return encoded_img.tobytes()