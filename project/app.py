""" Flask application to upload and anonymize documents containing personal data. """

import os
from flask import Flask, request, send_file, render_template
from pytesseract import pytesseract
from werkzeug.utils import secure_filename
from PIL import Image
import fitz  # PyMuPDF
import spacy
import personal_data_recognizer
import image_anonymizer
import text_recognizer

# Directory setup for file uploads and anonymized results
UPLOAD_FOLDER = 'uploads/'
ANONYMIZED_FOLDER = 'anonymized/'

# Create directories if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANONYMIZED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ANONYMIZED_FOLDER'] = ANONYMIZED_FOLDER


def recognize_text(image_path):
    """ Extracts text from given image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The extracted text from the image.
    """
    text = text_recognizer.extract_text_from_image(image_path, lang='rus')
    return text


def find_content_to_anonymize(file_path):
    """ Extracts personal data from document.

    Args:
        file_path (str): The path to the file (PDF or image).

    Returns:
        list: A list of anonymized strings found in the document.
    """
    analyzer = personal_data_recognizer.initialize_analyzer()
    text = ""
    if file_path.lower().endswith('.pdf'):
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
    else:
        text = text_recognizer.extract_text_from_image(file_path, lang='rus')
    return personal_data_recognizer.find_personal_data(text, analyzer)


@app.route('/')
def index():
    """ Главная страница с формой для загрузки файлов. """
    return render_template('/upload_form.html')


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
        content_to_anonymize = find_content_to_anonymize(file_path)

        anonymized_path = os.path.join(app.config['ANONYMIZED_FOLDER'], filename)
        if file_path.lower().endswith('.pdf'):
            # преобразовать в JPG
            print('d')
        else:
            image_anonymizer.anonymize_image(file_path, content_to_anonymize, anonymized_path)

        # with open(anonymized_path, 'w', encoding='utf-8') as f:
        #     f.write(" ".join(anonymized_content))

        return send_file(anonymized_path, as_attachment=True)
    return 'File processed', 200  # Ensure consistent return behavior


if __name__ == '__main__':
    app.run(debug=True)
