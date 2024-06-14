"""Module to anonymize personal data using Presidio Analyzer."""
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from spacy.tokens import Doc
import re

from text_preprocessor import preprocess


def initialize_analyzer():
    """
    Initialize analyzer engine.

    Returns:
      str: Analyzer engine.
    """

    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "ru", "model_name": "ru_core_news_lg"}]
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=['ru'])


def createc_doc_from_tokens(nlp, tokens):
    doc = Doc(nlp.vocab, words=tokens)
    doc = nlp.get_pipe('ner')(doc)
    return doc


def find_personal_data(text, analyzer):
    """
    Anonymize personal data in the input text.

    Args:
        text (str): The input text containing personal data.
        analyzer: Engine analyzer

    Returns:
        list: A list of found words consists personal data.

    Raises:
        ValueError: If the text is empty after preprocessing or if no entities are found.
    """
    regex_patterns = {
        'passport': r'\b\d{2} \d{6}\b',
        'snils': r'\b\d{3}-\d{3}-\d{3}[- ]?[А-Яа-яA-Za-z0-9]{2}\b',
        'phone': r'\+\d{1,3} \(\d{3}\) \d{3}-\d{2}-\d{2}',
        'email': r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b'
    }

    found_entities = []
    for pattern_name, pattern in regex_patterns.items():
        matches = re.findall(pattern, text)
        found_entities.extend(matches)

    token_sentences = preprocess(text)

    for sentence in token_sentences:
        if isinstance(sentence, list):
            sentence_str = " ".join(sentence)
        else:
            sentence_str = sentence

        result = analyzer.analyze(text=sentence_str, language='ru')
        found_entities.extend([sentence_str[obj.to_dict()['start']:obj.to_dict()['end']] for obj in result])

    return split_words_in_array(found_entities)


def split_words_in_array(array):
    """
    Split elements in the array into separate words if they contain more than one word.

    Args:
        array (list): The input array containing strings.

    Returns:
        list: A new array with elements split into separate words if they contain more than one word.
    """
    result = []
    for item in array:
        if len(re.findall(r'\w+', item)) > 1:
            result.extend(item.split())
        else:
            result.append(item)
    return result
