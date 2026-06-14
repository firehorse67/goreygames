#!/usr/bin/env python3
from pathlib import Path
from wordfreq import zipf_frequency

WORDS_FILE = Path("sextet_words.txt")   # full guess list
BAN_FILE   = Path("sextet_ban.txt")     # words never allowed as answers
KEEP_FILE  = Path("sextet_keep.txt")    # words always allowed as answers
OUT_FILE   = Path("sextet_answers.txt") # final answer list

# Minimum zipf frequency score for an answer word.
# Zipf scale: 6 = very common ("the"), 3 = moderately known, 0 = unknown.
# 3.0 gives ~2,600 answers of genuinely familiar words (comparable to NYT Wordle).
# Lower to 2.8 to add ~400 more less-common-but-valid words.
FREQ_THRESHOLD = 3.0


def load_word_set(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if not w:
                continue
            out.add(w)
    return out


def looks_ok_as_answer(word: str) -> bool:
    if len(word) != 6 or not word.isalpha():
        return False
    # Drop derivational suffixes that feel mechanical rather than core vocabulary.
    for suf in ("ish", "ness", "less"):
        if word.endswith(suf):
            return False
    return True


def main():
    all_words = load_word_set(WORDS_FILE)
    banned    = load_word_set(BAN_FILE)
    keep      = load_word_set(KEEP_FILE)

    # Basic heuristic filter
    candidates = {w for w in all_words if looks_ok_as_answer(w)}

    # Frequency filter: keep only words familiar enough for a casual game
    before_freq = len(candidates)
    candidates = {w for w in candidates if zipf_frequency(w, "en") >= FREQ_THRESHOLD}

    # Apply manual ban / keep overrides
    candidates -= banned
    candidates |= (keep & all_words)

    with OUT_FILE.open("w", encoding="utf-8") as out:
        for w in sorted(candidates):
            out.write(w + "\n")

    print(f"Guess words (total):  {len(all_words)}")
    print(f"After heuristics:     {before_freq}")
    print(f"After freq >= {FREQ_THRESHOLD}:    {len(candidates) + len(banned & candidates)}")
    print(f"Banned:               {len(banned)}")
    print(f"Kept (forced):        {len(keep & all_words)}")
    print(f"Final answer list:    {len(candidates)}  ->  {OUT_FILE}")


if __name__ == "__main__":
    main()
