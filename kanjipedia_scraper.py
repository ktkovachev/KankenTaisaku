import requests
import json
import time
import random
import functools
import operator
import regex as re
import os
import sys
from typing import Optional, Tuple

KANJI_URL_PATTERN = re.compile(r"/kanji/(\d+)")
PAGE_NUMBER_PATTERN = re.compile(r'<a href="/sakuin/\w+?/.+?/\d+">(\d+)</a>')
KOTOBA_RESULT_PATTERN = re.compile(r'(?:https://www.kanjipedia.jp)?/kotoba/(\d+)')

KANJI_SEARCH_BASE = "https://www.kanjipedia.jp/search"
INDEX_BASE = "https://www.kanjipedia.jp/sakuin"
YOJIJUKUGO_INDEX_NAME = "yojijyukugo"
KOTOWAZA_INDEX_NAME = "koji_kotowaza"
JUKUJIKUN_ATEJI_INDEX_NAME = "jyukujikun_ateji"

BASE_PATH = "kanjipedia"
KANJI_PATH = f"{BASE_PATH}/kanji"
YOJIJUKUGO_PATH = f"{BASE_PATH}/{YOJIJUKUGO_INDEX_NAME}"
KOTOWAZA_PATH = f"{BASE_PATH}/{KOTOWAZA_INDEX_NAME}"
JUKUJIKUN_ATEJI_PATH = f"{BASE_PATH}/{JUKUJIKUN_ATEJI_INDEX_NAME}"
KOTOBA_PATH = f"{BASE_PATH}/kotoba"

with open("supplementary/characters/kanken.json") as f:
    j = json.load(f)
    KANJI_LIST = functools.reduce(operator.add, (level["kanjiList"] for level in j))

with open("supplementary/characters/hiragana.json") as f:
    j = json.load(f)
    HIRAGANA = functools.reduce(operator.add, (item["kana"] for item in j if len(item["kana"]) == 1))

def pause_after_search():
    time.sleep(random.random())

def pause_after_fetch():
    t = random.random() + 1.5
    print(f"waiting {t:.0f} seconds...", end=" ", flush=True)
    time.sleep(t)
    print("done.")

def get_kanjipedia_url(kanji: str) -> Optional[str]:
    search = f"{KANJI_SEARCH_BASE}?k={kanji}&kt=1&sk=perfect"
    search_page = requests.get(search)
    try:
        return "https://www.kanjipedia.jp" + re.search(KANJI_URL_PATTERN, search_page.content.decode("utf-8")).group(0)
    except AttributeError:
        # Match does not exist
        return None

def get_local_path(kanji: str) -> str:
    return f"{KANJI_PATH}/{kanji}.html"

def fetch_kanji_to_file(kanji: str, path: str) -> None:
    print(f"Fetching {kanji}...", end=" ", flush=True)
    page_url = get_kanjipedia_url(kanji)
    if not page_url:
        print("no page found on Kanjipedia...")
        return
    print("found...", end=" ", flush=True)
    pause_after_search()
    data = requests.get(page_url)
    with open(path, mode="wb") as f:
        f.write(data.content)
    print("saved; ", end=" ", flush=True)
    pause_after_fetch()

def download_kanji() -> None:
    consecutive_failures = 0
    for kanji in KANJI_LIST:
        if len(kanji) == 3: kanji = kanji[1:-1] # Handle the 3 characters encoded as (填) etc.
        path = get_local_path(kanji)

        if os.path.exists(path):
            continue

        try:
            fetch_kanji_to_file(kanji, path)
            consecutive_failures = 0
        except KeyboardInterrupt:
            raise SystemExit(0)
        except Exception as e:
            print(e)
            print("Failed to download page for", kanji, "skipping for now", file=sys.stderr)
            if os.path.exists(path):
                os.remove(path)

            consecutive_failures += 1

            if consecutive_failures >= 1500:
                print("Over 1500 consecutive errors; quitting.", file=sys.stderr)
                raise SystemExit(1)
            continue

def get_index_url(index_name: str, kana: str, *, page: int = 1):
    url = f"{INDEX_BASE}/{index_name}/{kana}"
    if page != 1: url += f"/{page}"
    return url

def get_local_index_path(index_name: str):
    return f"{BASE_PATH}/indices/{index_name}"

# Returns: the number of pages for that index, plus the first page
def get_page_count(index_name: str, kana: str) -> Tuple[int, str]:
    page = requests.get(get_index_url(index_name, kana))
    content = page.content.decode()
    page_nums = [*PAGE_NUMBER_PATTERN.finditer(content)]

    max_page = 1
    if len(page_nums) != 0:
        max_page = int(max(page_nums, key=lambda m: int(m.group(1))).group(1))
    return (max_page, content)

# Returns: all links to "kotoba" (e.g. https://www.kanjipedia.jp/kotoba/0000020600) from a search page
def harvest_kotoba_links_from_search(search_page: str, save_location: str) -> None:
    for kotoba_match in KOTOBA_RESULT_PATTERN.finditer(search_page):
        for _ in range(5):
            try:
                kotoba_id = kotoba_match.group(1)
                file_save_location = f"{save_location}/{kotoba_id}.html"
                kotoba_url = f"https://www.kanjipedia.jp/kotoba/{kotoba_id}"
                if not os.path.exists(file_save_location):
                    response = requests.get(kotoba_url)
                    with open(file_save_location, mode="wb") as f:
                        f.write(response.content)
                    print(f"Saved {kotoba_id}.html...", end=" ", flush=False)
                    pause_after_fetch()
                else:
                    print(f"Skipping kotoba with ID {kotoba_id} as it already exists...", flush=False)
                break
            except Exception as e:
                print(e)
                print("Waiting 30 seconds before trying again...")
                time.sleep(30)
def download_index_generic(index_name: str, save_path: str) -> None:
    index_path = get_local_index_path(index_name)
    for kana in HIRAGANA:
        if any(page[0] == kana for page in os.listdir(index_path)):
            # Index has already been saved
            print(f"Skpping index {index_name} for {kana}...")
            continue
        else:
            print(f"Downloading {index_name} for {kana}...")

        print(f"Getting results for {kana}...", end=" ", flush=True)
        num_pages, first_page = get_page_count(index_name, kana)
        print(f"found {num_pages} page{'s' if num_pages != 1 else ''}...", end=" ", flush=True)
        with open(f"kanjipedia/indices/{index_name}/{kana}_page_1.html", mode="w") as f:
            f.write(first_page)

        for i in range(2, num_pages + 1):  # If the page count is more than 1, download the other pages of the index too
            index_page_url = get_index_url(index_name, kana, page=i)
            request = requests.get(index_page_url)
            with open(f"kanjipedia/indices/{index_name}/{kana}_page_{i}.html", mode="w") as f:
                f.write(request.content.decode())

    for index_page in os.listdir(index_path):
        print("Processing", index_page)
        with open(f"{index_path}/{index_page}") as f:
            index_content = f.read()
            for kotoba_link_match in KOTOBA_RESULT_PATTERN.finditer(index_content):
                kotoba_link = "https://www.kanjipedia.jp" + kotoba_link_match.group(0)
                file_save_path = f"{KOTOBA_PATH}/{index_name}/{kotoba_link_match.group(1)}.html"
                if os.path.exists(file_save_path):
                    continue
                kotoba_content = requests.get(kotoba_link).content.decode()
                
                with open(file_save_path, mode="w") as g:
                    print("Saving", file_save_path)
                    g.write(kotoba_content)


def download_yojijukugo() -> None:
    download_index_generic(YOJIJUKUGO_INDEX_NAME, YOJIJUKUGO_PATH)

def download_kotowaza() -> None:
    download_index_generic(KOTOWAZA_INDEX_NAME, KOTOWAZA_PATH)

def download_jukujikun_and_ateji() -> None:
    download_index_generic(JUKUJIKUN_ATEJI_INDEX_NAME, JUKUJIKUN_ATEJI_PATH)

def download_kotoba() -> None:
    print("Downloading kotoba from saved kanji pages...")
    SAVE_LOCATION = f"{KOTOBA_PATH}/kotoba"
    for kanji in os.listdir(KANJI_PATH):
        print(f"Getting kotoba from {kanji}...")
        with open(f"{KANJI_PATH}/{kanji}") as kanji_page:
            content = kanji_page.read()
            harvest_kotoba_links_from_search(content, SAVE_LOCATION)

def main():
    download_kanji(); print("Finished scraping kanji...")
    download_yojijukugo(); print("Finished scraping yojijukugo...")
    download_kotowaza(); print("Finished scraping kotowaza...")
    download_jukujikun_and_ateji(); print("Finished scraping jukujikun...")
    download_kotoba(); print("Finished downloading kotoba...")
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nQuit")