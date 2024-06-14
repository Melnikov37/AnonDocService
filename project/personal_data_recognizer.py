"""Module to anonymize personal data using Presidio Analyzer."""
import re

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine, NerModelConfiguration
from spacy.tokens import Doc

from text_preprocessor import preprocess

regex_patterns = {
    'PASSPORT': r'\b\d{2} \d{6}\b',
    'SNILS': r'\b\d{3}-\d{3}-\d{3}[- ]?[А-Яа-яA-Za-z0-9]{2}\b',
    'PHONE': r'\+\d{1,3} \(\d{3}\) \d{3}-\d{2}-\d{2}',
    'EMAIL': r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b',
    'DATE': r'\b\d{2}[./-]\d{2}[./-]\d{4}\b'
}

context_clues = {
    'PERSON': ['имя', 'фамилия', 'отчество', 'ф.и.о.', 'фио', 'врач', 'пациент', 'заведующий', 'врач-'],
    'LOCATION': ['место', 'жительства', 'адрес', 'прописка', 'прописки', 'регистрации'],
    'DATE': ['дата рождения', 'родился', 'родилась', 'др', 'день рождения', 'д.р.']
}


def initialize_analyzer():
    """
    Initialize analyzer engine.

    Returns:
      str: Analyzer engine.
    """

    model_config = [{"lang_code": "ru", "model_name": "ru_core_news_lg"}]
    ner_model_configuration = NerModelConfiguration(default_score=0.9)
    nlp_engine = SpacyNlpEngine(models=model_config, ner_model_configuration=ner_model_configuration)
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
    personal_data_found = []
    token_sentences = preprocess(text)

    for sentence in token_sentences:

        if isinstance(sentence, list):
            sentence_str = " ".join(sentence)
        else:
            sentence_str = sentence

        personal_data_found.extend(analyze_text_by_regex(sentence_str))
        personal_data_found.extend(analyze_by_nlp_engine(analyzer, sentence_str))

    return set(split_words_in_array(personal_data_found))


def analyze_by_nlp_engine(analyzer, sentence_str):
    found_entities = []
    result = analyzer.analyze(text=sentence_str, language='ru', score_threshold=0.9)

    for obj in result:
        entity = sentence_str[obj.to_dict()['start']:obj.to_dict()['end']]
        entity_type = obj.to_dict()['entity_type']

        if entity_type not in context_clues:
            found_entities.append(entity)
        else:
            clues = context_clues[entity_type]
            contextualized_opt = contextualize(clues, entity, sentence_str)

            if contextualized_opt is not None:
                found_entities.append(contextualized_opt)

    return found_entities


def contextualize(context_tips, context_element, context):
    """
    Analyze context clues to find matches.

    Args:
        context_tips (List[str]): List of context clues.
        context_element (str): Element for which it is necessary to check context membership.
        context (str): The context in which to search.

    Returns:
        Optional[str]: The context element if found, otherwise None.
    """
    for clue in context_tips:

        if (re.search(rf'{clue.lower()}.{{0,50}}{context_element.lower()}', context.lower())
                or re.search(rf'{context_element.lower()}.{{0,50}}{clue.lower()}', context.lower())):
            return context_element

    return None


def analyze_text_by_regex(text):
    matches_with_context = []

    for pattern_name, pattern in regex_patterns.items():
        matches = re.findall(pattern, text)

        if pattern_name not in context_clues:
            matches_with_context.extend(matches)
            continue

        clues = context_clues[pattern_name]

        for match in matches:
            contextualized_match_opt = contextualize(clues, match, text)

            if contextualized_match_opt is not None:
                matches_with_context.append(match)

    return matches_with_context


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
