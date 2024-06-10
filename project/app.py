from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re
import spacy

# Настройка директорий для загрузки и анонимизации файлов
UPLOAD_FOLDER = 'uploads/'
ANONYMIZED_FOLDER = 'anonymized/'

# Создание директорий, если они не существуют
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANONYMIZED_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ANONYMIZED_FOLDER'] = ANONYMIZED_FOLDER

nlp = spacy.load("ru_core_news_sm")

def anonymize_text(text):
    doc = nlp(text)
    anonymized_text = text
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'GPE', 'ORG']:
            anonymized_text = anonymized_text.replace(ent.text, '[ANONYMIZED]')
    anonymized_text = re.sub(r'\d{10}', '[PHONE]', anonymized_text)

    # Открытие файла для записи
    with open("output.txt", "w") as file:
        # Запись заголовка
        file.write("Token\tPOS\tTag\tLemma\n")

        # Запись токенов и их тегов
        for token in doc:
            file.write(f"{token.text}\t{token.pos_}\t{token.tag_}\t{token.lemma_}\n")

    return anonymized_text

def anonymize_document(file_path):
    anonymized_content = ""
    if file_path.lower().endswith('.pdf'):
        doc = fitz.open(file_path)
        for page in doc:
            text = page.get_text()
            anonymized_text = anonymize_text(text)
            anonymized_content += anonymized_text + "\n"
    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        anonymized_text = anonymize_text(text)
        anonymized_content = anonymized_text
    return anonymized_content

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    user_id = request.form.get('user_id')  # Получение параметра user_id из формы
    if user_id:
        print(f"Received user_id: {user_id}")

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        anonymized_content = anonymize_document(file_path)
        anonymized_path = os.path.join(app.config['ANONYMIZED_FOLDER'], filename)
        with open(anonymized_path, 'w', encoding='utf-8') as f:  # Указание кодировки UTF-8
            f.write(anonymized_content)
        return send_file(anonymized_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
