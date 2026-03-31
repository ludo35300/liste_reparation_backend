import cv2
import numpy as np

def load_image_from_bytes(file_bytes):
    arr = np.frombuffer(file_bytes, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def preprocess_for_ocr(img):
    gray     = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    binary   = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return binary

def crop_zone(img, x_pct, y_pct, w_pct, h_pct):
    h, w = img.shape[:2]
    x1, y1 = int(w * x_pct),           int(h * y_pct)
    x2, y2 = int(w * (x_pct + w_pct)), int(h * (y_pct + h_pct))
    return img[y1:y2, x1:x2]

def resize_for_ocr(img, max_width=2400):
    """Redimensionne l'image si trop grande pour économiser la RAM."""
    h, w = img.shape[:2]
    if w <= max_width:
        return img
    scale = max_width / w
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

