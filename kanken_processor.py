import os
import sys
import argparse
from typing import Iterable

from data_models import Kanji, Kotoba

CACHE_OBJECT_PATH = "build/kanjipedia_cache.pickle"
def parse_data_cached() -> tuple[Iterable[Kanji], Iterable[Kotoba]]:
    """Use pickling to cache parsed kanji/kotoba data on disk and retrieve it if already stored.
    If the data is over a certain age, it may be invalidated.
    """
    import pickle
    try:
        with open(CACHE_OBJECT_PATH, "rb") as f:
            kanji, kotoba = pickle.load(f)
            return kanji, kotoba
    except FileNotFoundError:
        from kanjipedia_collator import parse_all_kanji, parse_all_kotoba
        kanji, kotoba = list(parse_all_kanji()), list(parse_all_kotoba())
        with open(CACHE_OBJECT_PATH, "wb") as f:
            pickle.dump((kanji, kotoba), f)
        return kanji, kotoba

def generate_anki_deck():
    from anki_deck_generator import build_deck
    # from kanjipedia_collator import parse_all_kanji, parse_all_kotoba
    print("Building Anki deck...", file=sys.stderr)
    # package = build_deck(parse_all_kanji(), parse_all_kotoba())
    package = build_deck(*parse_data_cached())
    package.write_to_file("build/漢検一級.apkg")

def generate_data_files():
    # from kanjipedia_collator import parse_all_kanji, parse_all_kotoba
    print("Building static data files...", file=sys.stderr)

    def generate_dump(output_file: str, iterable: Iterable):
        with open(output_file, mode="w") as f:
            f.write("\n".join(str(item) for item in iterable))

    # all_kanji = parse_all_kanji()
    all_kanji, all_kotoba = parse_data_cached()
    generate_dump("build/kanji.tsv", all_kanji)

    # all_kotoba = parse_all_kotoba()
    generate_dump("build/kotoba.tsv", all_kotoba)

def main():
    cli_parser = argparse.ArgumentParser(
        prog="kanken-processor",
        description="Program that collates Kanken data",
    )
    cli_parser.add_argument("action", choices=["compile-data", "compile-deck", "compile-all"])
    cli_parser.add_argument("--purge-cache", action="store_true", dest="purge_cache")

    args = cli_parser.parse_args()

    # Remove the object storing the cache
    if args.purge_cache:
        try:
            os.remove(CACHE_OBJECT_PATH)
        except FileNotFoundError:
            pass

    action: str = args.action
    if action == "compile-data":
        generate_data_files()
    elif action == "compile-deck":
        generate_anki_deck()
    elif action == "compile-all":
        pass  # WIP
    else:
        print("Invalid action:", action, file=sys.stderr)

if __name__ == "__main__":
    main()