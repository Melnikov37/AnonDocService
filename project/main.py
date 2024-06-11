from image_anonymizer import anonymize_image

if __name__ == "__main__":
    input_image_path = "input.jpg"
    output_image_path = "output.jpg"
    words_to_anonymize = ["Рак", "14.04.2024", "Гематокрит"]

    anonymize_image(input_image_path, words_to_anonymize, output_image_path)
    print("Anonymization complete. Check the output image.")
