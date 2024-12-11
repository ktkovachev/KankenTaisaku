from collections import defaultdict
from dataclasses import dataclass, field
import subprocess
from typing import Optional
import regex as re

with open("kakikae.txt") as f:
    files = f.read().splitlines()

def grep_contents(filename: str) -> str:
    return subprocess.run(["grep", "rewrite", filename, "-A", "10", "-B", "10"], capture_output=True).stdout.decode()

kakikae_contents = map(grep_contents, files)

KAKIKAERAREU_PATTERN = re.compile(r"<p>(.+?)に書きかえられる|<p>(.+?)が書きかえ字")
KAKIKAERU_PATTERN = re.compile(r"<p>(.+?)の書きかえ字")

type kanji = str

@dataclass
class KakikaeRaw:
    rewrites: Optional[str] = field(default=None)
    rewritten_by: Optional[str] = field(default=None)

    def __str__(self):
        return f"{self.rewrites}/{self.rewritten_by}"

def filename_to_kanji(filename: str) -> kanji:
    return filename[-6]

manual_search_required = []
out: dict[kanji, KakikaeRaw] = defaultdict(KakikaeRaw)
for file, contents in zip(files, kakikae_contents):
    kanji_char = filename_to_kanji(file)
    kakikae, kakikaerare = KAKIKAERU_PATTERN.search(contents), KAKIKAERAREU_PATTERN.search(contents)
    if kakikae is None and kakikaerare is None:
        manual_search_required.append(file)
        print(contents)
        input()
        print("="*20)
    
    if kakikae:
        out[kanji_char].rewrites = kakikae.group(1)
    if kakikaerare:
        out[kanji_char].rewritten_by = kakikaerare.group(1) or kakikaerare.group(2)

assert len(manual_search_required) == 0

print("\n".join(f"{char}: {rewrite}" for char, rewrite in out.items()))

# # Postprocessing
# @dataclass
# class RewrittenSense:
#     rewrite_char: Optional[]
#     meaning: Optional[list[int]]