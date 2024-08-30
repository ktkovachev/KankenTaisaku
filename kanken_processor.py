import sys
import argparse
from typing import Iterable

def generate_anki_deck():
    from anki_deck_generator import build_deck
    from kanjipedia_collator import parse_all_kanji, parse_all_kotoba
    print("Building Anki deck...", file=sys.stderr)
    package = build_deck(parse_all_kanji(), parse_all_kotoba())
    package.write_to_file("build/漢検一級.apkg")

def generate_data_files():
    from kanjipedia_collator import parse_all_kanji, parse_all_kotoba
    print("Building static data files...", file=sys.stderr)

    def generate_dump(output_file: str, iterable: Iterable):
        with open(output_file, mode="w") as f:
            f.write("\n".join(str(item) for item in iterable))

    all_kanji = parse_all_kanji()
    generate_dump("build/kanji.tsv", all_kanji)

    all_kotoba = parse_all_kotoba()
    generate_dump("build/kotoba.tsv", all_kotoba)

def main():
    cli_parser = argparse.ArgumentParser(
        prog="kanken-processor",
        description="Program that collates Kanken data",
    )
    cli_parser.add_argument("action", choices=["compile-data", "compile-deck", "compile-all"])

    args = cli_parser.parse_args()

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