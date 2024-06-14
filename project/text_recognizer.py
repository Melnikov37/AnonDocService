"""Module to preprocess image and recognize text on it"""

import pytesseract
import cv2
import numpy as np
import platform
from PIL import Image, ImageEnhance

# Проверяем, является ли операционная система Ubuntu
if platform.system() == 'Linux':
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

def debug(message: str):
    """
    Print the debug message.

    Parameters:
    message (str): The debug message to be printed.
    """
    print(f"[DEBUG] {message}")

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess the input image to enhance it for text recognition.

    Parameters:
    image_path (str): The file path to the image to be preprocessed.

    Returns:
    np.ndarray: The preprocessed image as a binary image.
    """
    # Brighten the image
    preprocessed_image_path = "tmp.png"
    img = Image.open(image_path)
    # rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    brightener = ImageEnhance.Brightness(img)
    img = brightener.enhance(1.5)
    contranstener = ImageEnhance.Contrast(img)
    img = contranstener.enhance(1.5)
    sharpenner = ImageEnhance.Sharpness(img)
    img = sharpenner.enhance(1.5)
    # img.save(preprocessed_image_path)

    # img = cv2.imread(preprocessed_image_path, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # enhanced = clahe.apply(gray)

    # blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    # thresholded_image = cv2.adaptiveThreshold(
    #     blurred,
    #     255,
    #     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     cv2.THRESH_BINARY,
    #     25,
    #     10)

    return img

def extract_text_from_image(image_path: str, lang: str = 'rus') -> str:
    """
    Extract text from the input image using Tesseract OCR.

    Parameters:
    image_path (str): The file path to the image from which text needs to be extracted.
    lang (str): The language code to be used by Tesseract OCR. Default is 'rus' (Russian).

    Returns:
    str: The extracted text from the image.
    """
    preprocessed_image = preprocess_image(image_path)
    custom_config = r'--oem 1 --psm 11'
    text = pytesseract.image_to_string(preprocessed_image, lang=lang, config=custom_config)
    # debug(f"Extracted text: {text}")
    return text

def extract_data_from_image(image_path: str, lang: str = 'rus') -> dict:
    """
    Extract data as a pytesseract dictionary from the input image using Tesseract OCR.

    Parameters:
    image_path (str): The file path to the image from which data needs to be extracted.
    lang (str): The language code to be used by Tesseract OCR. Default is 'rus' (Russian).

    Returns:
    dict: The extracted data as a pytesseract dictionary from the image.
    """
    preprocessed_image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_data(
        preprocessed_image,
        lang=lang,
        config=custom_config,
        output_type=pytesseract.Output.DICT)

def extract_lines_from_image(image_path: str, lang: str = 'rus') -> list:
    """
    Extract lines of text from the input image using Tesseract OCR.

    Parameters:
    image_path (str): The file path to the image from which lines of text need to be extracted.
    lang (str): The language code to be used by Tesseract OCR. Default is 'rus' (Russian).

    Returns:
    list: The extracted lines of text from the image.
    """

    data = extract_data_from_image(image_path, lang=lang)

    lines = []
    current_line = []

    for i in range(len(data['text'])):
        text = data['text'][i]
        if not text.strip():
            continue

        left = data['left'][i]
        width = data['width'][i]

        if current_line:
            last_word = current_line[-1]
            last_word_right = last_word['left'] + last_word['width']

            if left < last_word_right or left - last_word_right > 50:
                lines.append(" ".join([word['text'] for word in current_line]))
                current_line = []

        current_line.append({'text': text, 'left': left, 'width': width})

    if current_line:
        lines.append(" ".join([word['text'] for word in current_line]))

    return lines