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
            51,
            6)
        cv2.imwrite("temp/2-threshold_image.jpg", threshold_image)
        kernel = np.ones((1, 1), np.uint8)
        dilate_image = cv2.dilate(threshold_image, kernel, iterations=1)
        cv2.imwrite("temp/3-dilate_image.jpg", dilate_image)
        kernel = np.ones((1, 1), np.uint8)
        erode_image = cv2.erode(dilate_image, kernel, iterations=1)
        cv2.imwrite("temp/4-erode_image.jpg", erode_image)
        morphologyEx_image = cv2.morphologyEx(erode_image, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite("temp/5-morphologyEx_image.jpg", morphologyEx_image)
        medianBlur_image = cv2.medianBlur(morphologyEx_image, 3)
        cv2.imwrite("temp/6-medianBlur_image.jpg", medianBlur_image)
        orc_text = pytesseract.image_to_string(medianBlur_image, lang='rus+eng')
        with open("temp/orc_text_with_threshold.txt", "w", encoding="utf-8") as file:
            file.write(orc_text)
        image = medianBlur_image

    image_fixed = deskew(image)
    cv2.imwrite("temp/7-image_fixed.jpg", image_fixed)

    text_boxes_image = find_text_boxes(image_fixed)

    return image_fixed


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
    _, threshold = cv2.threshold(image, 210, 230, cv2.THRESH_BINARY)
    cv2.imwrite("temp/bad_image_check.jpg", threshold)
    orc_text = pytesseract.image_to_string(threshold, lang='rus+eng')
    with open("temp/bad_image_check.txt", "w", encoding="utf-8") as file:
        file.write(orc_text)
    return len(orc_text) < 300

def remove_borders(image):
    cropped_image = image.copy()
    cropped_image2 = image.copy()
    # Преобразуем в серый цвет
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Применяем детектор границ Canny
    edges = cv2.Canny(gray, threshold1=30, threshold2=100)

    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Находим контур с максимальной площадью, предполагая, что это лист бумаги
    max_contour = max(contours, key=cv2.contourArea)

    # Обрезаем изображение
    x, y, w, h = cv2.boundingRect(max_contour)
    cv2.rectangle(cropped_image2,(x,y),(x+w,y+h),(0,255,0),2)
    cv2.imwrite("temp/boxes2.jpg", cropped_image2)
    cropped_image = image[y:y+h, x:x+w]
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return (cropped_image)

def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    blur = cv2.GaussianBlur(newImage, (9, 9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=2)

    # Find all contours
    contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    print (len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    cv2.imwrite("temp/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle

def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage

def deskew(cvImage):
    angle = getSkewAngle(cvImage)
    return rotateImage(cvImage, -1.0 * angle)

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
    custom_config = r'--oem 1 --psm 6'
    ocr_text = pytesseract.image_to_string(preprocessed_image, lang=lang, config=custom_config)
    return ocr_text, preprocessed_image

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
