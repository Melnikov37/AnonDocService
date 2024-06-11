""" Flask application to upload and anonymize documents containing personal data. """

import os
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import spacy
import personal_data_anonymizer
from test_recognizer import extract_text_from_image

# Directory setup for file uploads and anonymized results
UPLOAD_FOLDER = 'uploads/'
ANONYMIZED_FOLDER = 'anonymized/'

# Create directories if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANONYMIZED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ANONYMIZED_FOLDER'] = ANONYMIZED_FOLDER

nlp = spacy.load("ru_core_news_sm")

def recognize_text(image_path):
    """ Extracts text from given image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The extracted text from the image.
    """
    text = extract_text_from_image(image_path, lang='rus')
    return text

def anonymize_document(file_path):
    """ Extracts text from given file and anonymizes personal data.

    Args:
        file_path (str): The path to the file (PDF or image).

    Returns:
        set: A set of anonymized strings found in the document.
    """
    analyzer = personal_data_anonymizer.initialize_analyzer()
    text = ""
    if file_path.lower().endswith('.pdf'):
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)

    personal_data = personal_data_anonymizer.find_personal_data(text, analyzer)
    return personal_data


@app.route('/upload', methods=['POST'])
def upload_file():
    """ Handles file uploads and sends back anonymized content. """
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        anonymized_content = anonymize_document(file_path)
        anonymized_path = os.path.join(app.config['ANONYMIZED_FOLDER'], filename)
        with open(anonymized_path, 'w', encoding='utf-8') as f:
            f.write(" ".join(anonymized_content))
        return send_file(anonymized_path, as_attachment=True)
    return 'File processed', 200  # Ensure consistent return behavior


if __name__ == '__main__':
    app.run(debug=True)
