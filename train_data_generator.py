import random
from faker import Faker
import json

fake = Faker('ru_RU')  # Use Russian locale for more realistic data

# Define entity types
ENTITY_TYPES = ["PERSON", "PASSPORT", "EMAIL", "PHONE_NUMBER", "BIRTH_DATE"]

def generate_synthetic_data(num_samples):
    data = []
    for _ in range(num_samples):
        sentence = ""
        entities = []

        # Randomly choose the number of entities to include in the sentence
        num_entities = random.randint(1, 5)

        for _ in range(num_entities):
            entity_type = random.choice(ENTITY_TYPES)
            if entity_type == "PERSON":
                entity_text = fake.name()
            elif entity_type == "PASSPORT":
                entity_text = fake.bothify(text="??######")
            elif entity_type == "EMAIL":
                entity_text = fake.email()
            elif entity_type == "PHONE_NUMBER":
                entity_text = fake.phone_number()
            elif entity_type == "BIRTH_DATE":
                entity_text = fake.date_of_birth().strftime("%d-%m-%Y")

            start_idx = len(sentence)
            sentence += entity_text + " "
            end_idx = len(sentence) - 1

            entities.append((start_idx, end_idx, entity_type))

            sentence = sentence.strip() + "."
            data.append((sentence, {"entities": entities}))

    return data


if __name__ == '__main__':
    generate_synthetic_data(10000000)