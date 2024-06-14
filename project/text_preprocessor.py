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

    date_pattern = re.compile(r'\b\d{1,2}\.\d{1,2}\.\d{4}\b')
    for row in rows:
        dates = date_pattern.findall(row)

        for i, date in enumerate(dates):
            row = row.replace(date, f"__DATE{i}__")

        row = re.sub(r'[^\w\s]', '', row)

        for i, date in enumerate(dates):
            row = row.replace(date, f"__DATE{i}__")

        tokens = nltk.word_tokenize(row, lang)
        filtered_tokens = [word.lower() for word in tokens if not word in stopwords.words(lang)]

        for i, date in enumerate(dates):
            filtered_tokens = [date if token == f"__date{i}__" else token for token in filtered_tokens]

        filter_sentence = filtered_tokens
        cleaned_rows.append(filter_sentence)

    return cleaned_rows
