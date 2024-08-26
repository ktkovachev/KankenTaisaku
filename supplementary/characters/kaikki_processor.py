from collections import defaultdict
import json

USEFUL_KEYS = {"etymology_text", "word", "etymology_templates", "redirects"}
NECESSARY_KEYS = {"etymology_text", "word"}
out = defaultdict(list)
with open("kaikki.org-dictionary-Chinese-by-pos-character.jsonl") as f:
    for line in f:
        line_json = json.loads(line)
        char = line_json["word"]
        if all(key in line_json for key in NECESSARY_KEYS):
            filtered = {key: value for key, value in line_json.items() if key in USEFUL_KEYS}
            out[char].append(filtered)

with open("kanji_etymologies.json", "w") as f:
    f.write(json.dumps(out, ensure_ascii=False, indent=4))
