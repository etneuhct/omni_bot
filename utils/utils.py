import os
import custom_settings


def message_transformation(message: str):
    # Retourne un str sans certains car. speciaux et en minis.

    message = message.lower()
    replacements = [("é", "è", "ë", "ê"), ("à", "ä", "â"), ("ï", "î"), ("ü", "û", "ù"), ("ö", "ô"), ("ç",)]
    replaced = ["e", "a", "i", "u", "o", "c"]

    for i in range(len(replacements)):
        for letter in replacements[i]:
            message = message.replace(letter, replaced[i])
    return message


def get_dictionary_word(minimum: int, maximum: int, lang: str):
    dict_path = os.path.join(custom_settings.INPUT_PATH, "dictionaries/dict_{}.txt".format(lang))
    if not os.path.exists(dict_path):
        dict_path = os.path.join(custom_settings.INPUT_PATH, "dictionaries/dict_{}.txt".format('fr'))
    with open(dict_path, "r") as dictionary:
        dictionary = [word.lower() for word in dictionary.read().split("\n") if minimum < len(word) < maximum]
    return dictionary

