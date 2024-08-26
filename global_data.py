import json
from data_models import KaikkiKanjiData, ReadingSet

with open("supplementary/pronunciation/kanji_readings.json") as f:
    KANJI_READINGS: dict[str, ReadingSet] = json.load(f)

with open("supplementary/kanjipedia/bushu_image_to_unicode.json") as f:
    IMAGE_NAME_TO_RADICAL: dict[str, str] = json.load(f)

with open("supplementary/kanjipedia/headword_kanji_to_unicode.json") as f:
    HEADWORD_KANJI_TO_UNICODE: dict[str, str] = json.load(f)

with open("supplementary/characters/kanji_etymologies.json") as f:
    KANJI_ETYMOLOGIES = dict[str, list[KaikkiKanjiData]]