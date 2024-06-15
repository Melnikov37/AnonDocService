import cv2
import pytesseract
import platform
from typing import List
from text_recognizer import extract_lines_from_image, extract_text_from_image

# Проверяем, является ли операционная система Ubuntu
if platform.system() == 'Linux':
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


def anonymize_image(image_path: str, preprocess_image_path: str, words_to_anonymize: List[str],
                    output_path: str) -> None:
    """
    Anonymize specified words on the image by covering them with black rectangles.

    Args:
        image_path (str): Path to the input image.
        words_to_anonymize (List[str]): List of words to be anonymized.
        output_path (str): Path to save the anonymized image.
    """
    image = cv2.imread(preprocess_image_path)
    if image is None:
        raise FileNotFoundError(f"The image at path '{image_path}' could not be found.")
    # preprocess_image = cv2.imread(preprocess_image_path)
    # if preprocess_image is None:
    #     raise FileNotFoundError(f"The image at path '{preprocess_image_path}' could not be found.")

    #todo: эти данные нужно где-то кешить(слова - координаты слова)
    data_lines = extract_lines_from_image(preprocess_image_path, preprocessing_required=False)

    # Convert a two-dimensional list to a one-dimensional list
    data = [line for item in data_lines for line in item]

    for item in data:
        word = item['text']
        if word.lower() in words_to_anonymize:
            (x, y, w, h) = (item['left'], item['top'], item['width'], item['height'])
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
    return image
