import cv2
import pytesseract
import platform
from typing import List
from text_recognizer import extract_data_from_image

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
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"The image at path '{image_path}' could not be found.")
    preprocess_image = cv2.imread(preprocess_image_path)
    if preprocess_image is None:
        raise FileNotFoundError(f"The image at path '{preprocess_image_path}' could not be found.")

    #todo: эти данные нужно где-то кешить(слова - координаты слова)
    data = extract_data_from_image(image_path)

    n_boxes = len(data['text'])

    for i in range(n_boxes):

        word = data['text'][i]
        for word_to_anonymize in words_to_anonymize:
            if word_to_anonymize in word.lower():
                (x, y, w, h) = (data['left'][i], data['top'][i],
                                data['width'][i], data['height'][i])
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)

    return image
