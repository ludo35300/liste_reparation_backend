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