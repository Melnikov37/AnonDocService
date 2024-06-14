"""Module to preprocess image and recognize text on it"""

import pytesseract
import cv2
import numpy as np
import platform
from PIL import Image, ImageEnhance

# Проверяем, является ли операционная система Ubuntu
if platform.system() == 'Linux':
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess the input image to enhance it for text recognition.

    Parameters:
    image_path (str): The file path to the image to be preprocessed.

    Returns:
    np.ndarray: The preprocessed image as a binary image.
    """
    orc_text = "";
    image = cv2.imread(image_path)
    base_image = cv2.imread(image_path)
    cv2.imwrite("temp/0-image.jpg", image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("temp/1-gray.jpg", gray_image)
    orc_text = pytesseract.image_to_string(gray_image, lang='rus+eng')
    with open("temp/orc_text_base.txt", "w", encoding="utf-8") as file:
        file.write(orc_text)
    image = gray_image

    if bad_image_check(image):
        threshold_image = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            101,
            21)
        # threshold_image = cv2.threshold(
        #     image,
        #     0,
        #     255,
        #     cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        cv2.imwrite("temp/2-threshold_image.jpg", threshold_image)
        kernel = np.ones((1, 1), np.uint8)
        dilate_image = cv2.dilate(threshold_image, kernel, iterations=1)
        cv2.imwrite("temp/3-dilate_image.jpg", dilate_image)
        kernel = np.ones((1, 1), np.uint8)
        erode_image = cv2.erode(dilate_image, kernel, iterations=1)
        cv2.imwrite("temp/4-erode_image.jpg", erode_image)
        morphologyEx_image = cv2.morphologyEx(erode_image, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite("temp/5-morphologyEx_image.jpg", morphologyEx_image)
        medianBlur_image = cv2.medianBlur(morphologyEx_image, 1)
        cv2.imwrite("temp/6-medianBlur_image.jpg", medianBlur_image)
        orc_text = pytesseract.image_to_string(medianBlur_image, lang='rus+eng')
        with open("temp/orc_text_with_threshold.txt", "w", encoding="utf-8") as file:
            file.write(orc_text)
        image = medianBlur_image

    text_boxes_image = find_text_boxes(image)

    return image


def find_text_boxes(image):
    base_image = image.copy()
    blur = cv2.GaussianBlur(image, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 60))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cv2.imwrite("temp/find_text_boxes/dilate.jpg", dilate)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        roi = image[y:y+h, x:x + w]
        cv2.rectangle(base_image, (x, y), (x + w, y + h), (36, 255, 12), 2)

    cv2.imwrite("temp/find_text_boxes/image_with_border.jpg", base_image)
    return roi

def bad_image_check(image):
    blur = cv2.GaussianBlur(image, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 60))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    cv2.imwrite("temp/find_text_boxes/bad_image_check_dilate.jpg", dilate)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    max_contour = max(cnts, key=cv2.contourArea)
    perimeter = cv2.arcLength(max_contour, True)
    approx = cv2.approxPolyDP(max_contour, 0.02 * perimeter, True)

    return len(approx) < 6
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
    cv2.imwrite("temp/preprocessed_image.jpg", preprocessed_image)
    custom_config = r'--oem 3 --psm 1'
    ocr_text = pytesseract.image_to_string(preprocessed_image, lang=lang, config=custom_config)
    return ocr_text

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
    cv2.imwrite("temp/preprocessed_image.jpg", preprocessed_image)
    custom_config = r'--oem 3 --psm 1'
    return pytesseract.image_to_data(
        preprocessed_image,
        lang=lang,
        config=custom_config,
        output_type=pytesseract.Output.DICT)
