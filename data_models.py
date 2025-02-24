from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Self, TypedDict, Union


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

class RikuSho(IntEnum):
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
class BaseAndOkurigana:
    base: str  # Part that the kanji subsumes
    okurigana: str  # Okurigana part that is written in kana
    # Example: 重んじる has reading おも-んじる, where base = おも and okurigana = んじる

    @classmethod
    def parse_okurigana(cls, string: str) -> Self:
        if "-" not in string:
            string += "-"
        
        base, okurigana = string.split("-")
        return cls(base, okurigana)

    def __str__(self) -> str:
        return f"{self.base}-{self.okurigana}"
    
    def __hash__(self):
        return hash((self.base, self.okurigana))

    # def __dict__(self) -> dict:
    #     return {
    #         "base": self.base,
    #         "okurigana": self.okurigana
    #     }


@dataclass(init=False)
class Reading:
    reading: BaseAndOkurigana  # Literal reading
    in_kanken: bool  # Reading is found in the Kanken Kanji Jiten
    in_wiktionary: bool # Reading is found on EN Wiktionary
    is_hyougai: bool

    def __init__(self, reading: str, in_kanken: bool, in_wiktionary: bool, is_hyougai: bool = False):
        self.reading = BaseAndOkurigana.parse_okurigana(reading)
        self.in_kanken = in_kanken
        self.in_wiktionary = in_wiktionary
        self.is_hyougai = is_hyougai
    
    def __str__(self):
        return f"{self.reading}:{'k' if self.in_kanken else ''}{'w' if self.in_wiktionary else ''}{'h' if self.is_hyougai else ''}"

    # def __dict__(self) -> dict:
    #     return {
    #         "reading": dict(self.reading),
    #         "in_kanken": self.in_kanken,
    #         "in_wiktionary": self.in_wiktionary,
    #         "is_hyougai": self.is_hyougai
    #     }

# Temporarily use this class when parsing kun readings from Kanjipedia, as this information must later be collated into the overall
# `Reading` object, but the hyougai-pertaining information must be retained in the meantime.
@dataclass(init=False)
class KankenReading:
    reading: BaseAndOkurigana
    is_hyougai: bool

    def __init__(self, reading: str, is_hyougai: bool):
        self.reading = BaseAndOkurigana.parse_okurigana(reading)
        self.is_hyougai = is_hyougai
    
    def __hash__(self):
        return hash((self.reading, self.is_hyougai))

@dataclass
class Meaning:
    qualifier: str
    submeanings: list[str] # TODO: make class with "examples" attribute? Must ensure the format of entries roughly allows for this.

    def __str__(self):
        out = self.qualifier
        def_num = "①"
        for submeaning in self.submeanings:
            out += f"{def_num}{submeaning}"
            def_num = chr(ord(def_num)+1)  # Get next circled number
        return out

    @staticmethod
    def meaning_list_to_str(meaning_list: list[Self]) -> str:
        out = ""
        for meaning, circled_digit in zip(meaning_list, ("㊀", "㊁", "㊂", "㊃", "㊄")):
            out += circled_digit + str(meaning)
        return out

    # def __dict__(self) -> dict:
    #     return {
    #         "qualifier": self.qualifier,
    #         "submeanings": self.submeanings
    #     }

@dataclass
class Kanji:
    character: str
    level: KankenLevels
    is_kokuji: bool
    meanings: list[Meaning]
    on: list[Reading]
    goon: list[Reading]
    kanon: list[Reading]
    kanyoon: list[Reading]
    toon: list[Reading]
    soon: list[Reading]
    kun: list[Reading]
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
        return "; ".join(map(str, readings))
    
    @staticmethod
    def format_kanji_meaning_list(meanings: list[Meaning]) -> str:
        return Meaning.meaning_list_to_str(meanings)

    def as_tuple(self) -> tuple:
        return (
            self.character,
            str(self.level),
            str(int(self.is_kokuji)),  # 0 or 1
            self.format_kanji_meaning_list(self.meanings),
            self.format_kanji_reading_list(self.on),
            self.format_kanji_reading_list(self.goon),
            self.format_kanji_reading_list(self.kanon),
            self.format_kanji_reading_list(self.kanyoon),
            self.format_kanji_reading_list(self.toon),
            self.format_kanji_reading_list(self.soon),
            self.format_kanji_reading_list(self.kun),
            self.radical,
            str(self.strokes),
            str(self.added_strokes),
            str(self.glyph_origin),
            # self.replaces,
            # self.replaced_by
        )

    def __str__(self) -> str:
        return"\t".join(
            self.as_tuple()
        )

    # def __dict__(self) -> dict:
    #     return {
    #         "character": self.character,
    #         "level": str(self.level),
    #         "is_kokuji": self.is_kokuji,
    #         "meanings": list(map(dict, self.meanings)),
    #         "on": list(map(dict, self.on)),
    #         "goon": list(map(dict, self.goon)),
    #         "kanon": list(map(dict, self.kanon)),
    #         "kanyoon": list(map(dict, self.kanyoon)),
    #         "soon": list(map(dict, self.soon)),
    #         "toon": list(map(dict, self.toon)),
    #         "kun": list(map(dict, self.kun)),
    #         "radical": self.radical,
    #         "strokes": self.strokes,
    #         "added_strokes": self.added_strokes,
    #         "glyph_origin": str(self.glyph_origin),
    #         "replaces": self.replaces,
    #         "replaced_by": self.replaced_by,
    #     }

@dataclass
class Kanjitab:
    pass

@dataclass
class Kotoba:
    word: str
    reading: str  # List of readings?
    pitch_accent_pattern: list[str]  # 0 = heiban, other = pitch of mora preceding the accent drop; allow qualifiers such as (副)1 tentatively as strings
    meaning: str  # Definition as a paragraph
    is_jukujikun_ateji: bool  # If the word uses "irregular" readings
    kanjitab: Kanjitab

    @staticmethod
    def process_pitch_accent_patterns(pattern: list[str]) -> str:
        return ",".join(f"[{accent}]" for accent in pattern)

    def as_tuple(self) -> tuple:
        return (
            self.word,
            self.reading,
            self.process_pitch_accent_patterns(self.pitch_accent_pattern),
            self.meaning,
            str(int(self.is_jukujikun_ateji))
        )

    def __str__(self) -> str:
        return "\t".join(
            self.as_tuple()
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

class ReadingRecord(TypedDict):
    reading: str
    accent: list[str]  # More complicated, as the data includes e.g. (副)0,(名)1

class KaikkiTemplateData(TypedDict):
    name: str
    args: dict[str, str]
    expansion: str

class KaikkiKanjiData(TypedDict):
    redirects: list[str]
    etymology_text: str
    word: str
    etymology_templates: list[KaikkiTemplateData]
