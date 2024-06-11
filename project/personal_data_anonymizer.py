import spacy
from presidio_analyzer import AnalyzerEngine

from presidio_analyzer.nlp_engine import NlpEngineProvider

nlp = spacy.load("ru_core_news_lg")


def pre_process_text(input):
    words = input.split()
    normalized_text = ' '.join(words)
    return normalized_text


def find_personal_data(text):
    """
    Anonymize personal data in the input text.

    Args:
        text (str): The input text containing personal data.

     Returns:
        list: A list of found items as values.
    """
    text = pre_process_text(text)

    configuration = {"nlp_engine_name": "spacy", "models": [{"lang_code": "ru", "model_name": "ru_core_news_lg"}]}
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=['ru']
    )

    result = analyzer.analyze(text=text, language='ru')

    found_entities = [text[obj.to_dict()['start']:obj.to_dict()['end']] for obj in result]

    return set(found_entities)
