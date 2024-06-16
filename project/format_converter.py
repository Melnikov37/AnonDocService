import os

from pdf2image import convert_from_path
import os

def convert_pdf_to_jpg(pdf_path, output_folder):
    """Конвертирует PDF файл в изображения JPG, каждая страница становится отдельным файлом."""
    images = convert_from_path(pdf_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for i, image in enumerate(images):
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        image.save(f'{output_folder}/{filename}_page_{i + 1}.jpg', 'JPEG')

def convert_docx_to_pdf(docx_path, pdf_path):
    """Конвертирует DOCX файл в PDF. Требует установленного LibreOffice или Microsoft Office."""
    # Эта функция является заглушкой и должна быть реализована с учётом конкретной среды
    raise NotImplementedError("DOCX to PDF conversion requires specific environment setup.")

def convert_docx_to_jpg(docx_path, output_folder):
    """Конвертирует DOCX документ в JPG изображения через промежуточный PDF."""
    temp_pdf_path = f'{output_folder}/temp.pdf'
    convert_docx_to_pdf(docx_path, temp_pdf_path)
    convert_pdf_to_jpg(temp_pdf_path, output_folder)
    os.remove(temp_pdf_path)