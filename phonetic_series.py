import pywikibot
from tqdm import tqdm
import json

SITE = pywikibot.Site("en", "wiktionary")

BaxterSagart = str
ZhengzhangShangfang = str

# Literal page sources
def get_character_data_raw(char: str) -> tuple[BaxterSagart, ZhengzhangShangfang]:
    return (
        pywikibot.Page(SITE, f"Module:zh/data/och-pron-ZS/{char}").text,
        pywikibot.Page(SITE, f"Module:zh/data/och-pron-BS/{char}").text
    )

with open("supplementary/pronunciation/phonetic_series/group.json") as f:
    phonetic_series: dict[str, list[str]] = json.load(f)

data_dict = {}
for phonetic_component, characters in (bar := tqdm(phonetic_series.items())):
    for character in characters:
        bar.set_description(f"Getting {character}")
        data_dict[character] = get_character_data_raw(character)

# TODO: fix path / don't save at all? Or, use a dump.
with open("old-chinese-data.json", "w") as f:
    json.dump(data_dict, f, ensure_ascii=False, indent=4)

# TODO: process data further