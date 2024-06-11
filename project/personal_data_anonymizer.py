import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider


def load_nlp_model():
    return spacy.load("ru_core_news_lg")


def initialize_analyzer(nlp):
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "ru", "model_name": "ru_core_news_lg"}]
    }
    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=['ru'])


def normalize_spaces(input):
    """
    Normalize the input text by removing extra spaces.

    Args:
      input (str): The input text to normalize.

    Returns:
      str: The normalized text.
    """

    if not isinstance(input, str):
        raise ValueError("Input must be a string")

    return ' '.join(input.split())


def find_personal_data(text, analyzer):
    """
    Anonymize personal data in the input text.

    Args:
        text (str): The input text containing personal data.
        analyzer: Engine analyzer

    Returns:
        list: A list of found items as values.

    Raises:
        ValueError: If the text is empty after preprocessing or if no entities are found.
    """
    try:
        text = normalize_spaces(text)
        if not text:
            raise ValueError("Text is empty after preprocessing")
        result = analyzer.analyze(text=text, language='ru')
        found_entities = [text[obj.to_dict()['start']:obj.to_dict()['end']] for obj in result]
    except Exception as e:
        print(f"Error occurred while processing text: {e}")
        return []

    return set(found_entities)
