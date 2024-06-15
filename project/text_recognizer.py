"""Module to preprocess image and recognize text on it"""

import platform

import cv2
import numpy as np
import pytesseract

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
    #cv2.imwrite("temp/0-image.jpg", image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #cv2.imwrite("temp/1-gray.jpg", gray_image)
    #orc_text = pytesseract.image_to_string(gray_image, lang='rus+eng')
    #with open("temp/orc_text_base.txt", "w", encoding="utf-8") as file:
    #    file.write(orc_text)
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
        #cv2.imwrite("temp/2-threshold_image.jpg", threshold_image)
        kernel = np.ones((1, 1), np.uint8)
        dilate_image = cv2.dilate(threshold_image, kernel, iterations=1)
        #cv2.imwrite("temp/3-dilate_image.jpg", dilate_image)
        kernel = np.ones((1, 1), np.uint8)
        erode_image = cv2.erode(dilate_image, kernel, iterations=1)
        #cv2.imwrite("temp/4-erode_image.jpg", erode_image)
        morphologyEx_image = cv2.morphologyEx(erode_image, cv2.MORPH_CLOSE, kernel)
        #cv2.imwrite("temp/5-morphologyEx_image.jpg", morphologyEx_image)
        medianBlur_image = cv2.medianBlur(morphologyEx_image, 1)
        #cv2.imwrite("temp/6-medianBlur_image.jpg", medianBlur_image)
        #orc_text = pytesseract.image_to_string(medianBlur_image, lang='rus+eng')
        #with open("temp/orc_text_with_threshold.txt", "w", encoding="utf-8") as file:
        #    file.write(orc_text)
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
        roi = image[y:y + h, x:x + w]
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

    return len(approx) < 5

def extract_text_from_image(image_path: str, lang: str = 'rus', preprocessing_required: bool = True) -> str:
    """
    Extract text from the input image using Tesseract OCR.

    Parameters:
    image_path (str): The file path to the image from which text needs to be extracted.
    lang (str): The language code to be used by Tesseract OCR. Default is 'rus' (Russian).

    Returns:
    str: The extracted text from the image.
    """
    if preprocessing_required:
        image = preprocess_image(image_path)
    else:
        image = cv2.imread(image_path)
    cv2.imwrite("temp/preprocessed_image.jpg", image)
    custom_config = r'--oem 3 --psm 1'
    ocr_text = pytesseract.image_to_string(image, lang=lang, config=custom_config)
    return ocr_text


def extract_data_from_image(image_path: str, lang: str = 'rus', preprocessing_required: bool = True) -> dict:
    """
    Extract data as a pytesseract dictionary from the input image using Tesseract OCR.

    Parameters:
    image_path (str): The file path to the image from which data needs to be extracted.
    lang (str): The language code to be used by Tesseract OCR. Default is 'rus' (Russian).

    Returns:
    dict: The extracted data as a pytesseract dictionary from the image.
    """
    if preprocessing_required:
        image = preprocess_image(image_path)
    else:
        image = cv2.imread(image_path)
    cv2.imwrite("temp/preprocessed_image.jpg", image)
    custom_config = r'--oem 3 --psm 1'
    return pytesseract.image_to_data(
        image,
        lang=lang,
        config=custom_config,
        output_type=pytesseract.Output.DICT)


def extract_lines_from_image(image_path: str, lang: str = 'rus', preprocessing_required: bool = True) -> list:
    """
    Extract lines of text from the input image using Tesseract OCR.

    Parameters:
    image_path (str): The file path to the image from which lines of text need to be extracted.
    lang (str): The language code to be used by Tesseract OCR. Default is 'rus' (Russian).

    Returns:
    list: The extracted lines of text from the image.
    """

    data = extract_data_from_image(image_path, lang=lang, preprocessing_required=preprocessing_required)

    lines = []
    current_line = []

    for i in range(len(data['text'])):
        text = data['text'][i]
        if not text.strip():
            continue

        left = data['left'][i]
        width = data['width'][i]
        top = data['top'][i]
        height = data['height'][i]

        if current_line:
            last_word = current_line[-1]
            last_word_right = last_word['left'] + last_word['width']

            if left < last_word_right or left - last_word_right > 250:
                lines.append(current_line)
                current_line = []

        current_line.append({'text': text, 'left': left, 'width': width, 'top': top, 'height': height})

    if current_line:
        lines.append(current_line)

    return lines

def lines_to_text(lines):
    result = []
    for line in lines:
        result.append(" ".join([word['text'] for word in line]))
    return "\n".join(line for line in result)
