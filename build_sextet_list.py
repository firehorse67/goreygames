#!/usr/bin/env python3
from pathlib import Path

BASE_FILE = Path("wordlist.txt")      # your current list
EXTRA_FILE = Path("sextet_extra.txt")   # optional manual additions
OUT_FILE  = Path("sextet_words.txt")    # final file for the game

# Very common proper nouns / abbrevs to exclude even if lowercase
PROPER_LIKE = {
    "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday",
    "january", "february", "march", "april", "august",
    "september", "october", "november", "december",
    "british", "english"
}

def load_words(path: Path) -> set[str]:
    if not path.exists():
        return set()
    words = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if not w:
                continue
            words.add(w)
    return words

def acceptable(word: str) -> bool:
    # length must be 6
    if len(word) != 6:
        return False
    # pure letters only (no hyphens, apostrophes, etc.)
    if not word.isalpha():
        return False
    # no words ending in 's' (drops plurals and 3rd-person verbs)
    if word.endswith("s"):
        return False
    # no obvious proper nouns (you can expand this set)
    if word in PROPER_LIKE:
        return False
    # a crude extra guard: drop words that look like acronyms
    # (your source is already lowercase, but this is cheap)
    if not word.islower():
        return False
    return True

def main():
    base = load_words(BASE_FILE)
    extra = load_words(EXTRA_FILE)

    # merge and filter
    all_words = base | extra
    cleaned = {w for w in all_words if acceptable(w)}

    # write one word per line, sorted
    with OUT_FILE.open("w", encoding="utf-8") as out:
        for w in sorted(cleaned):
            out.write(w + "\n")

    print(f"Input base: {len(base)} words")
    print(f"Extra:      {len(extra)} words")
    print(f"Output:     {len(cleaned)} words -> {OUT_FILE}")

if __name__ == "__main__":
    main()
