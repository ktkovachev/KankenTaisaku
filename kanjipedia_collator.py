import regex as re
import os.path
import bs4
from tqdm import tqdm
from data_models import GlyphOrigin, Kanji, Kanjitab, KankenLevels, Kotoba, RikuSho
from global_data import KANJI_READINGS, IMAGE_NAME_TO_RADICAL, HEADWORD_KANJI_TO_UNICODE, KANJI_ETYMOLOGIES, PITCH_ACCENTS, SPECIAL_IMAGE_EXCEPTIONS

def compile_yojijukugo() -> list[str]:
    yoji_pattern = re.compile(r'<div id="kotobaArea">[\s\S]+?<p>.*?(\w{4})<\/p>\s*<p class="kotobaYomi">(\w+)<\/p>')
    spelling_note_pattern = re.compile(r'<sup>.+?</sup>')
    angle_brackets_pattern = re.compile(r'〈|〉')
    gaiji_pattern = re.compile(r'<img src="/common/images/kanji/\d+/std_(.+?)\.png">')
    out = []
    for file in os.listdir("kanjipedia/kotoba/yojijyukugo"):
        relative_path = os.path.join("kanjipedia/kotoba/yojijyukugo", file)
        with open(relative_path) as f:
            content = f.read()
            content = spelling_note_pattern.sub("", content)  # Strip these two which get in the way of the regex
            content = angle_brackets_pattern.sub("", content)
            content = gaiji_pattern.sub(lambda m: chr(int(m.group(1), 16)), content)  # Replace gaiji images with their corresponding Unicode character
            m = yoji_pattern.search(content)
            out.append(m.group(1))
    return out

IMAGE_OYAJI_PATTERN = re.compile(r'<p id="kanjiOyaji"><img src="/common/images/kanji/180/(nw|std)_(.+)\.png"></p>')
def convert_kanji_image(page_data: str, parser: bs4.BeautifulSoup) -> str:
    if (text := parser.find(id="kanjiOyaji").text):
        return text
    elif (m := IMAGE_OYAJI_PATTERN.search(page_data)):
        image_type = m.group(1)  # 'nw' or 'std'; 'nw' is special and apparently arbitrary, so needs look-up
        if image_type == "std":
            kanji_code = m.group(2)

            if kanji_code in SPECIAL_IMAGE_EXCEPTIONS:
                return SPECIAL_IMAGE_EXCEPTIONS[kanji_code]

            return chr(int(kanji_code, 16))  # The kanji image file is just named after its own Unicode codepoint
        else:
            num = m.group(2)
            try:
                return HEADWORD_KANJI_TO_UNICODE[num]
            except:
                print(page_data)
                raise Exception(num)
    else:
        raise Exception("Kanji could not be retrieved")

# Parsing kanji
def parse_single_kanji(page_data: str) -> Kanji:
    """Return an as-yet incomplete (with some fields yet to be populated) Kanji object.
    The reason it must be incomplete is because updated "shitatsuki" (and other) data
    must be able to be added to the Kanji object from other sources, i.e.
    the rest of the program should be able to add related compounds to the given fields
    once some Kotoba have been parsed already.
    """
    parser = bs4.BeautifulSoup(page_data, "html.parser")

    
    kanji = convert_kanji_image(page_data, parser)
    level = KankenLevels.str_to_enum(re.search(r'alt="(準?\d{1,2})級"', page_data).group(1))
    is_kokuji = bool(parser.find("img", src="/common/images/icon_kokuji.gif"))
    
    # Fetch reading data (from Wiktionary) TODO: specifically highlight which ones are Kanken
    readings = KANJI_READINGS[kanji]
    goon = readings["goon"]
    kanon = readings["kanon"]
    kanyoon = readings["kanyoon"]
    soon = readings["soon"]
    toon = readings["toon"]
    on = readings["on"]
    kun = readings["kun"]

    # Kanji trivia
    bushu_image = parser.find("p", attrs={"class": "kanjiBushu"}).find_next("img").attrs["src"]
    numeric_radical_code = os.path.splitext(os.path.split(bushu_image)[1])[0]
    radical = IMAGE_NAME_TO_RADICAL[numeric_radical_code]
    
    stroke_count = re.search(r'画数：\((\d+)\)', page_data).group(1)
    added_stroke_count = re.search(r'部首内画数(\d+)', page_data).group(1)

    kanji_right_section = parser.find(id="kanjiRightSection")
    meanings = kanji_right_section.findChild("div").text.strip().replace("\n", "<br>")

    if (origin_head := parser.find(href="https://promo.kadokawa.co.jp/shinjigen/")) and (
        (origin_explanation := origin_head.find_next("p"))
    ):
        origin = GlyphOrigin(RikuSho.ARBITRARY, origin_explanation.text.strip())
    else:
        if kanji in KANJI_ETYMOLOGIES:
            # TODO: extract the etymology from the etymology templates and give a precise etymology
            pass
        origin = GlyphOrigin(RikuSho.UNKNOWN, None)


    return Kanji(
        character=kanji,
        level=level,
        is_kokuji=is_kokuji,
        meanings=meanings,
        on=on,
        goon=goon,
        kanon=kanon,
        kanyoon=kanyoon,
        toon=toon,
        soon=soon,
        kun=kun,
        # uetsuki=[],  # UNSUPPLIED
        # shitatsuki=[],  # UNSUPPLIED
        radical=radical,
        strokes=stroke_count,
        added_strokes=added_stroke_count,
        glyph_origin=origin,
        replaced_by=[],
        replaces=[]
    )

def parse_all_kanji(save_path: str = "kanjipedia/kanji") -> list[Kanji]:
    out = []
    for file in tqdm(os.listdir(save_path)):
        file_path = os.path.join(save_path, file)
        with open(file_path) as f:
            out.append(parse_single_kanji(f.read()))
    return out

USAGE_SYMBOL_PATTERN = re.compile(r"[▲△〈〉]")
def strip_usage_symbols(headword: str) -> str:
    """Remove the following symbols:
        ▲ (referring to a reading of a jōyō kanji, which is not in the jōyō reading list)
        △ (denoting a non-jōyō kanji)
        〈〉 (encircling ateji or jukujikun entries)
    """
    return USAGE_SYMBOL_PATTERN.sub("", headword)

ATEJI_JUKUJI_HEADWORD_PATTERN = re.compile(r"〈.+〉")
def has_ateji_or_jukujikun(headword: str) -> bool:
    return bool(ATEJI_JUKUJI_HEADWORD_PATTERN.search(headword))  # Appears anywhere in the word, for any potential edge case

COLUMN_RUBRIC_PATTERN = re.compile(r"■コラムを読んでみよう\n.+")
def parse_single_kotoba(page_data: str) -> Kotoba:
    parser = bs4.BeautifulSoup(page_data, "html.parser")
    
    headline_div = parser.find("div", id="kotobaArea")
    word = headline_div.find_next("p").text
    reading = headline_div.find_next("p").find_next("p").text
    
    is_jukujikun_ateji = has_ateji_or_jukujikun(word)
    word = strip_usage_symbols(word)

    meaning = parser.find("div", id="kotobaExplanationSection").text.strip()
    meaning = COLUMN_RUBRIC_PATTERN.sub("", meaning)  # Remove kanji article advertisements
    meaning = meaning.replace("\n", "<br>")  # Encode newlines without using the delimiting \n character

    pitch_accent_pattern = PITCH_ACCENTS.get(word, {"accent": []})["accent"]  # If no accents found, just give an empty list

    return Kotoba(
        word=word,
        reading=reading,
        pitch_accent_pattern=pitch_accent_pattern,
        meaning=meaning,
        is_jukujikun_ateji=is_jukujikun_ateji,
        kanjitab=Kanjitab()
    )

def parse_all_kotoba(save_path: str = "kanjipedia/kotoba/kotoba") -> list[Kotoba]:
    out = []
    for file in tqdm(os.listdir(save_path)):
        file_path = os.path.join(save_path, file)
        with open(file_path) as f:
            out.append(parse_single_kotoba(f.read()))
    return out
