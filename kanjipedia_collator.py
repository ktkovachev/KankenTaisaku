import regex as re
import os.path
import bs4
from tqdm import tqdm
from data_models import GlyphOrigin, Kanji, KankenLevels, RikuSho
from global_data import KANJI_READINGS, IMAGE_NAME_TO_RADICAL, HEADWORD_KANJI_TO_UNICODE, KANJI_ETYMOLOGIES

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
            return chr(int(kanji_code, 16))
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
