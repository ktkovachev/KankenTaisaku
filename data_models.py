from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import TypedDict, Union


class KankenLevels(IntEnum):
    TEN = auto()
    NINE = auto()
    EIGHT = auto()
    SEVEN = auto()
    SIX = auto()
    FIVE = auto()
    FOUR = auto()
    THREE = auto()
    PRE_TWO = auto()
    TWO = auto()
    PRE_ONE = auto()
    ONE = auto()

    @classmethod
    def int_to_enum(cls, i: int):
        return list(cls)[i]

    @classmethod
    def str_to_enum(cls, name: str):
        return {
            "10": cls.TEN,
            "9": cls.NINE,
            "8": cls.EIGHT,
            "7": cls.SEVEN,
            "6": cls.SIX,
            "5": cls.FIVE,
            "4": cls.FOUR,
            "3": cls.THREE,
            "準2": cls.PRE_TWO,
            "2": cls.TWO,
            "準1": cls.PRE_ONE,
            "1": cls.ONE
        }[name]

    @staticmethod
    def is_jouyou(level) -> bool:
        return level <= KankenLevels.TWO
    
    @staticmethod
    def is_kyouiku(level) -> bool:
        return level <= KankenLevels.FIVE

    def __str__(self) -> str:
        return {
            self.TEN: "10",
            self.NINE: "9" ,
            self.EIGHT: "8",
            self.SEVEN: "7",
            self.SIX: "6",
            self.FIVE: "5",
            self.FOUR: "4",
            self.THREE: "3",
            self.PRE_TWO: "準2",
            self.TWO: "2",
            self.PRE_ONE: "準1",
            self.ONE: "1",
        }[self]

class RikuSho(Enum):
    PICTOGRAPH = auto()
    IDEOGRAPH = auto()
    IDEOGRAPHIC_COMPOUND = auto()
    PHONO_SEMANTIC_COMPOUND = auto()
    ARBITRARY = auto()
    UNKNOWN = auto()

@dataclass
class Pictograph:
    description: str

@dataclass
class Ideograph:
    description: str

@dataclass
class IdeographicCompound:
    characters: list[str]
    description: str

@dataclass
class PhonoSemanticCompound:
    characters: list[str]
    description: list[str]

@dataclass
class GlyphOrigin:
    type: RikuSho
    origin: Union[Pictograph, Ideograph, IdeographicCompound, PhonoSemanticCompound, str]

    def __str__(self) -> str:
        if self.type is RikuSho.IDEOGRAPH:
            return f"指事 {self.origin}"
        elif self.type is RikuSho.PICTOGRAPH:
            return f"象形 {self.origin}"
        elif self.type is RikuSho.IDEOGRAPHIC_COMPOUND:
            return f"会意 {'＋'.join(self.origin.characters)}"
        elif self.type is RikuSho.PHONO_SEMANTIC_COMPOUND:
            return f"形声 音符{self.origin.characters[0]} ＋ {'＋'.join(self.origin.characters[1:])}"
        elif self.type is RikuSho.UNKNOWN:
            return "説明無し"
        else:
            # Verbatim origin
            return self.origin

KANJI_LEVELS: dict[str, str] = {
    "漢": KankenLevels.EIGHT,
    "字": KankenLevels.TEN
}

@dataclass
class Kanji:
    character: str
    level: KankenLevels
    is_kokuji: bool
    meanings: str  # For now, a paragraph or sequence thereof, just in plain text.
    on: list[str]
    goon: list[str]
    kanon: list[str]
    kanyoon: list[str]
    toon: list[str]
    soon: list[str]
    kun: list[str]
    # uetsuki: list[str]
    # shitatsuki: list[str]
    radical: str
    strokes: int
    added_strokes: int
    glyph_origin: GlyphOrigin
    replaces: list[str]
    replaced_by: list[str]

    @property
    def is_jouyou(self) -> bool:
        return KankenLevels.is_jouyou(self.level)

    @property
    def is_kyouiku(self) -> bool:
        return KankenLevels.is_kyouiku(self.level)
    
    @staticmethod
    def format_kanji_reading_list(readings: list[str]) -> str:
        return "; ".join(readings)

    def __str__(self) -> str:
        return"\t".join(
            (
                self.character,
                str(self.level),
                str(int(self.is_kokuji)),  # 0 or 1
                self.meanings,
                self.format_kanji_reading_list(self.on),
                self.format_kanji_reading_list(self.goon),
                self.format_kanji_reading_list(self.kanon),
                self.format_kanji_reading_list(self.kanyoon),
                self.format_kanji_reading_list(self.toon),
                self.format_kanji_reading_list(self.soon),
                self.format_kanji_reading_list(self.kun),
                self.radical,
                str(self.glyph_origin),
            )
        )

def kanken_level_single(kanji: str) -> str:
    return KANJI_LEVELS[kanji]

def kanken_level(word: str) -> str:
    return max(map(kanken_level_single, word))


class ReadingSet(TypedDict):
    goon: list[str]
    kanon: list[str]
    toon: list[str]
    soon: list[str]
    kanyoon: list[str]
    on: list[str]
    kun: list[str]
    nanori: list[str]

class KaikkiTemplateData(TypedDict):
    name: str
    args: dict[str, str]
    expansion: str

class KaikkiKanjiData(TypedDict):
    redirects: list[str]
    etymology_text: str
    word: str
    etymology_templates: list[KaikkiTemplateData]