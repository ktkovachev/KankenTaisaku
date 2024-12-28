from typing import Iterable
import genanki
import os.path

from data_models import Kanji, Kotoba

KANJI_MODEL_ID = 1976405439
KOTOBA_MODEL_ID = 1616488250

# NOTE: May use part-of-speech-differentiated card variants in the future.
# VERB_MODEL_ID = 1844777987
# ADJECTIVE_MODEL_ID = 1118383897
# YOJIJUKUGO_MODEL_ID = 1116935715
# INDECLINABLE_MODEL_ID = 1753028315

KANKEN_DECK_ID = 1169437805
KANKEN_KANJI_SUBDECK_ID = 1228308188
KANKEN_KOTOBA_SUBDECK_ID = 1095745966

def load_generic(file_path: str):
    with open(file_path) as f:
        return f.read()

def load_template(template_name: str):
    return load_generic(os.path.join("anki", "templates", template_name))

def load_style(template_name: str):
    return load_generic(os.path.join("anki", "styles", template_name))


KANJI_MODEL = genanki.Model(
    KANJI_MODEL_ID,
    "Kanken Kanji",
    fields=[
        {"name": "Kanji"},
        {"name": "Level"},
        {"name": "Is kokuji?"},
        {"name": "Meanings"},
        {"name": "Unclassified on"},
        {"name": "Go-on"},
        {"name": "Kan-on"},
        {"name": "Kan'yō-on"},
        {"name": "Tō-on"},
        {"name": "Sō-on"},
        {"name": "Kun"},
        # {"name": "Uetsuki"},
        # {"name": "Shitatsuki"},
        {"name": "Radical"},
        {"name": "Stroke count"},
        {"name": "Radical-added stroke count"},
        # {"name": "JIS"},
        {"name": "Glyph origin"},
        # {"name": "Replaces"},
        # {"name": "Replaced by"},
        # {"name": "Simplified forms"},
        # {"name": "Traditional forms"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": load_template("kanji_front.html"),
            "afmt": load_template("kanji_back.html")
        }
    ],
    css=load_style("kanji.css")
)

KOTOBA_MODEL = genanki.Model(
    KOTOBA_MODEL_ID,
    "Kanken Kotoba",
        fields=[
            {"name": "Word"},
            {"name": "Reading"},
            {"name": "Pitch accents pattern(s)"},
            {"name": "Meanings"},
            {"name": "Is jukujikun/ateji?"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": load_template("kanji_front.html"),
                "afmt": load_template("kanji_back.html")
            }
        ],
        css=load_style("kotoba.css")
)


class KanjiNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0]) # The character field only

class KotobaNote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0]) # The word field only

def create_kanji_note(kanji: Kanji) -> KanjiNote:
    return KanjiNote(
        KANJI_MODEL,
        fields=kanji.as_tuple()
    )

def create_kotoba_note(kotoba: Kotoba) -> KotobaNote:
    return KotobaNote(
        KOTOBA_MODEL,
        fields=kotoba.as_tuple()
    )

def build_deck(kanjis: Iterable[Kanji], kotobas: Iterable[Kotoba]) -> genanki.Package:
    # Currently appears to be unnecessary, as cards are only sorted into the subdecks, not the main deck
    kanken_deck = genanki.Deck(
        KANKEN_DECK_ID,
        "漢検一級"
    )

    kanken_kanji_subdeck = genanki.Deck(
        KANKEN_KANJI_SUBDECK_ID,
        "漢検一級::漢字"
    )

    kanken_kotoba_subdeck = genanki.Deck(
        KANKEN_KOTOBA_SUBDECK_ID,
        "漢検一級::言葉"
    )

    for kanji in kanjis:
        note = create_kanji_note(kanji)
        kanken_kanji_subdeck.add_note(note)

    for kotoba in kotobas:
        note = create_kotoba_note(kotoba)
        kanken_kotoba_subdeck.add_note(note)
    
    package = genanki.Package([kanken_kanji_subdeck, kanken_kotoba_subdeck])
    return package
