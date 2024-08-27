import sys
import argparse

def generate_anki_deck():
    from anki_deck_generator import build_deck
    print("Building Anki deck...", file=sys.stderr)
    pass

def generate_data_files():
    from kanjipedia_collator import parse_all_kanji, parse_all_kotoba

    # all_kanji = parse_all_kanji()
    # with open("build/kanji.tsv", mode="w") as f:
    #     f.write("\n".join(str(kanji) for kanji in all_kanji))

    all_kotoba = parse_all_kotoba()
    with open("build/kotoba.tsv", mode="w") as f:
        f.write("\n".join(str(kotoba) for kotoba in all_kotoba))

def main():
    cli_parser = argparse.ArgumentParser(
        prog="kanken-processor",
        description="Program that collates Kanken data",
    )
    cli_parser.add_argument("action", choices=["compile-data", "compile-deck"])

    args = cli_parser.parse_args()

    action: str = args.action
    if action == "compile-data":
        generate_data_files()
    elif action == "compile-deck":
        generate_anki_deck()
    else:
        print("Invalid action:", action, file=sys.stderr)

if __name__ == "__main__":
    main()