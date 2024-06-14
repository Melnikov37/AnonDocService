import re

import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
from nltk.corpus import stopwords


def extract_sentences_by_newline(text):
    return text.split('\n')


def preprocess(text, lang='russian'):
    rows = extract_sentences_by_newline(text)
    cleaned_rows = []

    for row in rows:
        row = re.sub(r'\.(?=\s|$)', '', row)
        row = re.sub(r'(?<!\w)[^\w\s.-]+(?!\w)', '', row)
        row = re.sub(r'(?<!\w)[^\w\s.-]+|[^\w\s.-]+(?!\w)', '', row)

        tokens = nltk.word_tokenize(row, lang)
        filtered_tokens = [word.lower() for word in tokens if not word in stopwords.words(lang)]

        filter_sentence = filtered_tokens
        cleaned_rows.append(filter_sentence)

    return cleaned_rows
