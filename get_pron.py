import re
import requests
import sys
from pathlib import Path


def word_url(word: str) -> str:
    return f"https://sakura-paris.kovachev.xyz/%EF%BC%AE%EF%BC%A8%EF%BC%AB%E3%80%80%E6%97%A5%E6%9C%AC%E8%AA%9E%E7%99%BA%E9%9F%B3%E3%82%A2%E3%82%AF%E3%82%BB%E3%83%B3%E3%83%88%E8%BE%9E%E5%85%B8/exact/{word}"


def audio_url(audio_part: str) -> str:
    return f"https://sakura-paris.kovachev.xyz{audio_part}"


def req_word(word: str) -> requests.Response:
    return requests.get(word_url(word))


WAV_LINK_PATTERN = re.compile(r'title="発音図："><source src="(.*?/[^/]+\.wav)"')


def get_audio_link(resp: requests.Response) -> str | None:
    m = WAV_LINK_PATTERN.search(resp.text)
    if m is None:
        return None
    else:
        return m.group(1)


def download_wav(url: str) -> bytes:
    return requests.get(url).content


def save_wav(word: str, output: Path):
    r = req_word(word)
    audio_file_path = get_audio_link(r)
    if audio_file_path is None:
        print("Error: no audio found for", word, file=sys.stderr)
        return
    audio_link = audio_url(audio_file_path)
    wav_bytes = download_wav(audio_link)
    with open(output, "wb") as f:
        f.write(wav_bytes)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs="?")
    parser.add_argument("-o", default="output.wav", metavar="o")

    args = parser.parse_args()

    if not args.word:
        word = input("Enter word to get audio for: ")
    else:
        word = args.word
    out_path = Path(args.o)
    save_wav(word, out_path)


if __name__ == "__main__":
    main()
