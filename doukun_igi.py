import regex as re
import json

HOMOPHONIC_GROUP_PATTERN = re.compile(r'<a href="/sakuin/doukunigi/items/\d+">\s+<span>(.+)</span><br>\s+((?:\s\w)+)')
KANAS = "あかさたなはまやらわ"

def main():
    homophonic_groups: dict[list[str], list[str]] = {}
    for kana in KANAS:
        html_file_path = f"kanjipedia/indices/doukun_igi/{kana}.html"
        with open(html_file_path) as f:
            contents = f.read()
        
        for match in HOMOPHONIC_GROUP_PATTERN.finditer(contents):
            kun, kanji_list = match.groups()
            homophonic_groups[kun] = list(map(str.strip, kanji_list.split(" ")))
    
    with open("build/doukun_igigo.json", mode="w") as f:
        json.dump(homophonic_groups, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()