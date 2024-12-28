import dataclasses
import json
import os
from pathlib import Path
import pickle
import sys
import argparse
from typing import Iterable, Optional

from data_models import Kanji, Kotoba

KANJI_CACHE_OBJECT_PATH = Path("build/cache/kanji_cache.pickle")
KOTOBA_CACHE_OBJECT_PATH = Path("build/cache/kotoba_cache.pickle")
def load_pickle(path: Path) -> Optional[object]:
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
            return obj
    except FileNotFoundError:
        return None

def dump_pickle(path: Path, obj: object) -> None:
    with open(path, "wb") as f:
        pickle.dump(obj, f)

def parse_data_cached() -> tuple[Iterable[Kanji], Iterable[Kotoba]]:
    """Use pickling to cache parsed kanji/kotoba data on disk and retrieve it if already stored.
    If the data is over a certain age, or some other conditions are met, it may be invalidated. (Not yet implemented.)
    """
    kanji = load_pickle(KANJI_CACHE_OBJECT_PATH)
    kotoba = load_pickle(KOTOBA_CACHE_OBJECT_PATH)
    
    if kanji is None:
        from kanjipedia_collator import parse_all_kanji
        print("Parsing kanji from Kanjipedia dump...", file=sys.stderr)
        kanji = list(parse_all_kanji())
        dump_pickle(KANJI_CACHE_OBJECT_PATH, kanji)
        
    if kotoba is None:    
        from kanjipedia_collator import parse_all_kotoba
        print("Parsing kotoba from Kanjipedia dump...", file=sys.stderr)
        kotoba = list(parse_all_kotoba())
        dump_pickle(KOTOBA_CACHE_OBJECT_PATH, kotoba)

    return kanji, kotoba

def generate_anki_deck():
    from anki_deck_generator import build_deck
    print("Building Anki deck...", file=sys.stderr)
    package = build_deck(*parse_data_cached())
    package.write_to_file("build/anki/漢検一級.apkg")

def generate_tsv_files():
    print("Building TSV files...", file=sys.stderr)

    def generate_dump(output_file: str, iterable: Iterable):
        with open(output_file, mode="w") as f:
            f.write("\n".join(str(item) for item in iterable))

    all_kanji, all_kotoba = parse_data_cached()
    generate_dump("build/tsv/kanji.tsv", all_kanji)
    generate_dump("build/tsv/kotoba.tsv", all_kotoba)

def generate_json_files():
    print("Building JSON files...", file=sys.stderr)

    def generate_dump(output_file: str, iterable: Iterable):
        with open(output_file, mode="w") as f:
            f.write("\n".join(json.dumps(dataclasses.asdict(item), ensure_ascii=False) for item in iterable))

    all_kanji, all_kotoba = parse_data_cached()
    generate_dump("build/json/kanji.jsonl", all_kanji)
    generate_dump("build/json/kotoba.jsonl", all_kotoba)

def main():
    cli_parser = argparse.ArgumentParser(
        prog="kanken-processor",
        description="Program that collates Kanken data",
    )
    cli_parser.add_argument("action", choices=["compile-tsv", "compile-json", "compile-deck", "compile-all"])
    cli_parser.add_argument("--purge-cache", action="store_true", dest="purge_cache")

    args = cli_parser.parse_args()

    # Remove the object storing the cache
    if args.purge_cache and input("Really delete cached data? ") in ("y", "yes"):
        try:
            os.remove(CACHE_OBJECT_PATH)
        except FileNotFoundError:
            pass

    action: str = args.action
    if action == "compile-tsv":
        generate_tsv_files()
    elif action == "compile-json":
        generate_json_files()
    elif action == "compile-deck":
        generate_anki_deck()
    elif action == "compile-all":
        pass  # WIP
    else:
        print("Invalid action:", action, file=sys.stderr)

if __name__ == "__main__":
    main()