from collections import defaultdict
import json
from tqdm import tqdm
from typing import TypedDict

class ReadingRecord(TypedDict):
    reading: str
    # accent: list[int]
    accent: list[str]  # More complicated, as the data includes e.g. (副)0,(名)1

def main():
    out: dict[str, ReadingRecord] = defaultdict(ReadingRecord)
    with open("accents.tsv") as f:
        for line in tqdm(f):
            word, reading, accent = line[:-1].split("\t")
            # accent = list(map(int, accent.split(",")))
            accent = accent.split(",")
            out[word] = ReadingRecord(reading=reading, accent=accent)

    with open("accents.json", mode="w") as f:
        json.dump(out, f, ensure_ascii=False)

if __name__ == "__main__":
    main()