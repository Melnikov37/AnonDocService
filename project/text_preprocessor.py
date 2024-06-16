import re

import nltk

from nltk.corpus import stopwords


def extract_sentences_by_newline(text):
    return text.split('\n')


def preprocess(text, lang='russian'):
    rows = extract_sentences_by_newline(text)
    cleaned_rows = []

    stop_words = stopwords.words(lang)

    for row in rows:
        row = re.sub(r'\.(?=\s|$)', '', row)
        row = re.sub(r'(?<!\w)[^\w\s.-]+(?!\w)', '', row)
        row = re.sub(r'(?<!\w)[^\w\s.-]+|[^\w\s.-]+(?!\w)', '', row)

        tokens = nltk.word_tokenize(row, lang)
        filtered_tokens = []
        for word in tokens:
            nlp_word_minimum_length = 2
            word_lower = word.lower()
            if (len(word_lower) <= nlp_word_minimum_length or word_lower in stop_words):
                continue
            filtered_tokens.append(word_lower)

        cleaned_rows.append(filtered_tokens)

    return cleaned_rows
