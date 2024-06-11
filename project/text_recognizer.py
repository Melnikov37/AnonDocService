"""Module to preprocess image and recognize text on it"""

from PIL import Image, ImageEnhance
import pytesseract
import cv2
import os

def preprocess_image(image_path):
    # Brighten the image
    preprocessed_image_path = "tmp.png"
    img = Image.open(image_path)

    brightener = ImageEnhance.Brightness(img)
    img = brightener.enhance(1.5)
    contranstener = ImageEnhance.Contrast(img)
    img = contranstener.enhance(1.5)
    sharpenner = ImageEnhance.Sharpness(img)
    img = sharpenner.enhance(1.5)
    
    img.save(preprocessed_image_path)

    img = cv2.imread(preprocessed_image_path, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresholded_image = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 10)

    return thresholded_image

def extract_text_from_image(image_path, lang='rus'):
    preprocessed_image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(preprocessed_image, lang=lang, config=custom_config)
