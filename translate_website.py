"""
translate_website.py
Batch-translates the website's en.json master file into all target
languages using the Google Cloud Translate API v2 (same key/pattern as
the PC Analyzer's translate_locales.py).

Run locally on Dave's machine (needs internet access to
translation.googleapis.com, which Claude's sandbox cannot reach).

Usage:
    python translate_website.py

Requires:
    pip install requests

Output:
    locales/<lang_code>.json for every language in TARGET_LANGUAGES,
    written next to this script. Also copies en.json itself into
    locales/en.json so the loader always has an English fallback.
"""

import json
import os
import time
import requests

# ---- CONFIG ----------------------------------------------------------

API_KEY = "AIzaSyAmW60joi2Acfwp_5--R6BlJWfCdjkxOSA"  # current restricted key
SOURCE_FILE = "en.json"
OUTPUT_DIR = "locales"

# Master list — matches PC Analyzer's locales folder exactly.
# 'en' and 'iw' are skipped for translation ('en' is the source itself,
# 'iw' is the legacy Hebrew code — duplicate of 'he'). Remove that
# skip if you decide you want 'iw' generated as a duplicate too.
TARGET_LANGUAGES = [
    "af", "ar", "az", "bg", "bn", "ceb", "cs", "cy", "da", "de", "el",
    "es", "et", "eu", "fa", "fi", "fr", "ga", "gl", "gu", "he", "hi",
    "hr", "hu", "hy", "id", "is", "it", "ja", "ka", "ko", "lt", "lv",
    "mr", "ms", "mt", "nl", "no", "pl", "ps", "pt", "ro", "ru", "sk",
    "sl", "sr", "sv", "ta", "th", "tl", "tr", "uk", "ur", "vi",
    "zh-CN", "zh-TW",
]

TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"

# ---- SCRIPT ------------------------------------------------------------

def load_source():
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def translate_batch(texts, target_lang):
    """Translate a list of strings in one API call. Returns list in same order."""
    params = {
        "key": API_KEY,
        "q": texts,
        "target": target_lang,
        "source": "en",
        "format": "text",
    }
    resp = requests.post(TRANSLATE_URL, data=params)
    resp.raise_for_status()
    data = resp.json()
    return [t["translatedText"] for t in data["data"]["translations"]]


def main():
    source = load_source()
    keys = list(source.keys())
    values = list(source.values())

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Always keep an English copy in locales/ for the loader's default/fallback
    with open(os.path.join(OUTPUT_DIR, "en.json"), "w", encoding="utf-8") as f:
        json.dump(source, f, ensure_ascii=False, indent=2)
    print("Wrote locales/en.json (source copy)")

    for lang in TARGET_LANGUAGES:
        out_path = os.path.join(OUTPUT_DIR, f"{lang}.json")
        try:
            translated_values = translate_batch(values, lang)
            translated = dict(zip(keys, translated_values))
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(translated, f, ensure_ascii=False, indent=2)
            print(f"OK   {lang} -> {out_path}")
        except Exception as e:
            print(f"FAIL {lang}: {e}")
        time.sleep(0.3)  # gentle pacing, avoid rate limits

    print("\nDone. Upload the locales/ folder to the website repo root.")


if __name__ == "__main__":
    main()
