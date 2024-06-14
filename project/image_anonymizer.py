import cv2
import pytesseract
import platform
from typing import List

# Проверяем, является ли операционная система Ubuntu
if platform.system() == 'Linux':
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


def anonymize_image(image_path: str, preprocess_image_path: str, words_to_anonymize: List[str], output_path: str) -> None:
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

    data = pytesseract.image_to_data(preprocess_image, lang='rus', output_type=pytesseract.Output.DICT)

    confidence_threshold = 60

    n_boxes = len(data['text'])

    for i in range(n_boxes):
        if int(data['conf'][i]) > confidence_threshold:
            word = data['text'][i]
            if word.lower() in words_to_anonymize:
                (x, y, w, h) = (data['left'][i], data['top'][i],
                                data['width'][i], data['height'][i])
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)

    return image
