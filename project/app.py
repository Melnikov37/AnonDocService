""" Flask application to upload and anonymize documents containing personal data. """

import os
import shutil

import cv2
import fitz  # PyMuPDF
from flask import Flask, request, send_file, render_template
from PIL import Image
import image_anonymizer
import personal_data_recognizer
import text_recognizer
import format_converter as converter
import zipfile

# Directory setup for file uploads and anonymized results
UPLOAD_FOLDER = 'uploads/'
ANONYMIZED_FOLDER = 'anonymized/'
TEMP_FOLDER = 'temp/'
PDF_TO_JPG_FOLDER = 'pdf2jpg/'

# Create directories if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANONYMIZED_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(PDF_TO_JPG_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ANONYMIZED_FOLDER'] = ANONYMIZED_FOLDER
app.config['PDF_2_JPG_FOLDER'] = PDF_TO_JPG_FOLDER


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
    personal_data = personal_data_recognizer.find_personal_data(text, analyzer)
    return personal_data

def zip_anonymized_images(images):
    zip_filename = "anonymized_images.zip"
    zip_filepath = os.path.join(app.config['ANONYMIZED_FOLDER'], zip_filename)

    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for i,processed_image in enumerate(images):
                temp_filename = os.path.join(app.config['ANONYMIZED_FOLDER'], f'temp_image_{i}.jpg')
                im = Image.fromarray(processed_image)
                im.save(temp_filename)

                arcname = f'Image_{i}.jpg'
                zipf.write(temp_filename, arcname)

                # Optionally, remove the temporary file after adding it to the zip archive
                os.remove(temp_filename)
    return zip_filepath


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

        # file_list = os.listdir(app.config['UPLOAD_FOLDER'])
        # for filename in file_list:
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    content_to_anonymize = find_content_to_anonymize(file_path)

    anonymized_path = os.path.join(app.config['ANONYMIZED_FOLDER'], filename)
    if file_path.lower().endswith('.pdf'):
        # преобразовать в JPG
       anonymized_path = process_pdf(file_path, content_to_anonymize, app.config['PDF_2_JPG_FOLDER'])
    else:
        image = image_anonymizer.anonymize_image(file_path, "temp/preprocessed_image.jpg", content_to_anonymize)
        cv2.imwrite(anonymized_path, image)

    # with open(anonymized_path, 'w', encoding='utf-8') as f:
    #     f.write(" ".join(anonymized_content))

    return send_file(anonymized_path, as_attachment=True)
    # return 'File processed', 200  # Ensure consistent return behavior


def process_pdf(file_path, content_to_anonymize, pdf_to_jpg_folder):
    """Process PDF file by converting to JPG and anonymizing each page."""

    # Convert PDF to JPG
    try:
        converter.convert_pdf_to_jpg(file_path, pdf_to_jpg_folder)

        images_to_process = os.listdir(pdf_to_jpg_folder)
        processed_images = []

        for image in images_to_process:
            image_path = os.path.join(pdf_to_jpg_folder, image)
            processed_image = image_anonymizer.anonymize_image(image_path, image_path, content_to_anonymize)
            processed_images.append(processed_image)

        # Zip the anonymized images and return the zip path
        return zip_anonymized_images(processed_images)
    finally:
        clean_directory(pdf_to_jpg_folder)


def clean_directory(directory):
    """Remove all files in the specified directory."""

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

if __name__ == '__main__':
    app.run(debug=True)
