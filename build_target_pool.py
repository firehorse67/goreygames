#!/usr/bin/env python3
"""Rebuild target_pool.txt — the precomputed Target puzzles.

Each output line is "WORD CENTER". A 9-letter word from target_final.txt
qualifies if it is reasonably common (zipf >= FREQ_THRESHOLD, so the
full-marks answer is always a word people have met) and some centre letter
yields at least MIN_WORDS findable words from the scoring dictionary
(target_common.txt). Among qualifying centres the one with the *fewest*
findable words is chosen, which keeps puzzle sizes — and the effort needed
for an Excellent rank — consistent from game to game.

Run after changing target_final.txt, target_full.txt, target_ban.txt or the
threshold in build_target_common.py (rebuild target_common.txt first):

    python build_target_common.py
    python build_target_pool.py

Requires the wordfreq package:  pip install wordfreq
"""
from collections import Counter
from pathlib import Path
from wordfreq import zipf_frequency

FINAL_FILE  = Path("target_final.txt")    # candidate 9-letter words
FULL_FILE   = Path("target_full.txt")     # full accept dictionary
COMMON_FILE = Path("target_common.txt")   # scoring dictionary
BAN_FILE    = Path("target_ban.txt")      # words never used as puzzles
OUT_FILE    = Path("target_pool.txt")

MIN_WORDS = 40        # minimum findable (scoring) words per puzzle
FREQ_THRESHOLD = 2.7  # minimum zipf frequency for the 9-letter answer


def load_words(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [w.strip().lower() for w in path.open("r", encoding="utf-8") if w.strip()]


def is_excluded_plural(word: str, full: set[str]) -> bool:
    """Mirror the in-game plural filter: drop S-plurals whose base is a word."""
    if not word.endswith("s") or word.endswith("ss"):
        return False
    base = word[:-1]
    return base in full or base + "e" in full


def main():
    full = set(load_words(FULL_FILE))
    banned = set(load_words(BAN_FILE))
    common = [
        w for w in load_words(COMMON_FILE)
        if len(w) >= 4 and not is_excluded_plural(w, full)
    ]
    # Precompute letter data for the scoring words once.
    common_data = [(w, Counter(w), set(w)) for w in common]

    candidates = sorted({
        w for w in load_words(FINAL_FILE)
        if len(w) == 9 and w.isalpha() and w in full and w not in banned
        and not is_excluded_plural(w, full)
        and zipf_frequency(w, "en") >= FREQ_THRESHOLD
    })

    puzzles = []
    for cand in candidates:
        avail = Counter(cand)
        letter_set = set(cand)
        counts = Counter()
        for w, wc, ws in common_data:
            if not ws <= letter_set:
                continue
            if wc - avail:  # needs more of some letter than the puzzle has
                continue
            for c in ws:
                counts[c] += 1
        viable = {c: n for c, n in counts.items() if n >= MIN_WORDS}
        if not viable:
            continue
        centre = min(viable, key=lambda c: (viable[c], c))
        puzzles.append((cand, centre, viable[centre]))

    with OUT_FILE.open("w", encoding="utf-8") as out:
        for word, centre, _ in puzzles:
            out.write(f"{word.upper()} {centre.upper()}\n")

    sizes = sorted(n for _, _, n in puzzles)
    print(f"Candidate 9-letter words (freq >= {FREQ_THRESHOLD}): {len(candidates)}")
    print(f"Puzzles written:      {len(puzzles)}  ->  {OUT_FILE}")
    if sizes:
        mid = sizes[len(sizes) // 2]
        print(f"Findable words/puzzle: min {sizes[0]}, median {mid}, max {sizes[-1]}")


if __name__ == "__main__":
    main()
