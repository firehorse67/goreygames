#!/usr/bin/env python3
"""Build target_common.txt — the Target *scoring* dictionary.

The game accepts guesses against the full dictionary (target_full.txt) but
scores against this smaller list of words a typical player has actually met:
the word total, the rank thresholds and the Missed list all come from here.
Obscure-but-valid guesses are still accepted in-game as bonus words, so
trimming this list never rejects anyone's legitimate word.

Requires the wordfreq package:  pip install wordfreq
"""
from pathlib import Path
from wordfreq import zipf_frequency

FULL_FILE = Path("target_full.txt")     # full accept dictionary
BAN_FILE  = Path("target_ban.txt")      # never scored (still accepted as guesses)
KEEP_FILE = Path("target_keep.txt")     # always scored, regardless of frequency
OUT_FILE  = Path("target_common.txt")   # scoring dictionary for the game

# Minimum zipf frequency for a word to count toward scoring.
# 2.4 keeps ~22,000 of the ~69,000 full-dictionary words. Raise to 2.7 for a
# stricter list (~17,500), lower to 2.2 for a more generous one (~25,000).
# Words below this still count as bonus, so lowering it mainly moves familiar
# mid-frequency words (e.g. RIVET, OGLE, POACH, ABATE) from bonus into scoring.
# After changing this, rebuild the puzzle pool too: python build_target_pool.py
FREQ_THRESHOLD = 2.4


def load_word_set(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if w:
                out.add(w)
    return out


def main():
    full = load_word_set(FULL_FILE)
    banned = load_word_set(BAN_FILE)
    keep = load_word_set(KEEP_FILE)

    common = {
        w for w in full
        if len(w) >= 4 and w.isalpha() and zipf_frequency(w, "en") >= FREQ_THRESHOLD
    }
    common -= banned
    common |= (keep & full)

    with OUT_FILE.open("w", encoding="utf-8") as out:
        for w in sorted(common):
            out.write(w + "\n")

    print(f"Full dictionary:      {len(full)}")
    print(f"Banned:               {len(banned)}")
    print(f"Kept (forced):        {len(keep & full)}")
    print(f"Scoring dictionary:   {len(common)}  ->  {OUT_FILE}")


if __name__ == "__main__":
    main()
