"""Module to preprocess image and recognize text on it"""

import platform
import os

import cv2
import numpy as np
import pytesseract

# Проверяем, является ли операционная система Ubuntu
if platform.system() == 'Linux':
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

TEMP_FOLDER = 'temp/'
LOG_ON = True

os.makedirs(TEMP_FOLDER, exist_ok=True)

def preprocess_image(image_path: str) -> np.ndarray:
    """
    Preprocess the input image to enhance it for text recognition.

    Parameters:
    image_path (str): The file path to the image to be preprocessed.

    Returns:
    np.ndarray: The preprocessed image as a binary image.
    """



    filename = os.path.splitext(os.path.basename(image_path))[0]
    file_folder = os.path.join(TEMP_FOLDER, filename)
    os.makedirs(file_folder, exist_ok=True)

    orc_text = "";
    image = cv2.imread(image_path)
    base_image = cv2.imread(image_path)
    log_image(image, filename, '0-image.jpg')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    log_image(gray_image, filename, '1-gray.jpg')
    log_text(gray_image, filename, '1-gray-image-orc-text.txt')
    image = gray_image

    if bad_image_check(image, image_path):
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
        log_image(threshold_image, filename, '2-threshold_image.jpg')
        kernel = np.ones((1, 1), np.uint8)
        dilate_image = cv2.dilate(threshold_image, kernel, iterations=1)
        log_image(dilate_image, filename, '3-dilate_image.jpg')
        kernel = np.ones((1, 1), np.uint8)
        erode_image = cv2.erode(dilate_image, kernel, iterations=1)
        log_image(erode_image, filename, '4-erode_image.jpg')
        morphologyEx_image = cv2.morphologyEx(erode_image, cv2.MORPH_CLOSE, kernel)
        log_image(morphologyEx_image, filename, '5-morphologyEx_image.jpg')
        medianBlur_image = cv2.medianBlur(morphologyEx_image, 1)
        log_image(medianBlur_image, filename, '6-medianBlur_image.jpg')
        log_text(medianBlur_image, filename, '6-medianBlur_image-orc-text.txt')
        image = medianBlur_image
    # else:
    #     _, binary_image = cv2.threshold(image, 140, 255, cv2.THRESH_BINARY)
    #     log_image(binary_image, filename, '2-threshold_image.jpg')
    #     log_text(binary_image, filename, '2-threshold-image-orc-text.txt')
    #     image = binary_image

    text_boxes_image = find_text_boxes(image, image_path)

    return image

def log_image(image, filename, image_name):
    if LOG_ON:
        cv2.imwrite(os.path.join(TEMP_FOLDER, filename, image_name), image)

def log_text(image, filename, text_name):
    if LOG_ON:
        text = pytesseract.image_to_string(image, lang='rus')
        with open(os.path.join(TEMP_FOLDER, filename, text_name), "w", encoding="utf-8") as file:
            file.write(text)

def find_text_boxes(image, image_path):
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
        roi = image[y:y + h, x:x + w]
        cv2.rectangle(base_image, (x, y), (x + w, y + h), (36, 255, 12), 2)

    filename = os.path.splitext(os.path.basename(image_path))[0]
    file_folder = os.path.join(TEMP_FOLDER, filename, 'find_text_boxes')
    os.makedirs(file_folder, exist_ok=True)
    cv2.imwrite(os.path.join(file_folder, 'image_with_border.jpg'), base_image)
    return roi


def bad_image_check(image, image_path):
    blur = cv2.GaussianBlur(image, (7, 7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 60))
    dilate = cv2.dilate(thresh, kernal, iterations=1)
    filename = os.path.splitext(os.path.basename(image_path))[0]
    file_folder = os.path.join(TEMP_FOLDER, filename, 'find_text_boxes')
    os.makedirs(file_folder, exist_ok=True)
    cv2.imwrite(os.path.join(file_folder, 'bad_image_check_dilate.jpg'), dilate)

    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[1])

    max_contour = max(cnts, key=cv2.contourArea)
    perimeter = cv2.arcLength(max_contour, True)
    approx = cv2.approxPolyDP(max_contour, 0.02 * perimeter, True)

    return len(approx) < 5

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
    custom_config = r'--oem 3 --psm 6'
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
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_data(
        preprocessed_image,
        lang=lang,
        config=custom_config,
        output_type=pytesseract.Output.DICT)
