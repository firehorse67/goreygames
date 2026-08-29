#!/usr/bin/env python3
"""Build target_common.txt — the Target *scoring* dictionary.

The game accepts guesses against the full dictionary (target_full.txt) but
scores against this smaller list of words a typical player has actually met:
the word total, the rank thresholds and the Missed list all come from here.
Obscure-but-valid guesses are still accepted in-game as bonus words, so
trimming this list never rejects anyone's legitimate word.

After the frequency filter a second pass promotes common inflections (-ed,
-ing, -er, -est and their y→i variants) whose base form already scored.
This compensates for wordfreq underscoring regular inflected forms (e.g.
PRIED scores much lower than PRY).

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

# Inflection-boost settings.  A word NOT meeting FREQ_THRESHOLD can still be
# promoted to scored if it is a regular inflection of a word that IS scored.
# MIN_INFLECTION_FREQ:  the inflection itself must appear in real text (filters
#                       out ghost entries like WITHED, PEOPLER, etc.).
# MAX_BASE_FREQ:        excludes function words (WITH, HAVE, JUST, WILL …)
#                       whose obscure verb senses produce junk inflections.
MIN_INFLECTION_FREQ = 1.5
MAX_BASE_FREQ = 5.0


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


def _derive_bases(word: str) -> list[str]:
    """Return candidate base forms for standard English inflection patterns."""
    out: list[str] = []
    w = word
    if w.endswith("ied") and len(w) >= 5:
        out.append(w[:-3] + "y")
    if w.endswith("ier") and len(w) >= 5:
        out.append(w[:-3] + "y")
    if w.endswith("iest") and len(w) >= 6:
        out.append(w[:-4] + "y")
    if w.endswith("ed") and not w.endswith("ied") and len(w) >= 5:
        out.extend([w[:-1], w[:-2]])                # hoped→hope, packed→pack
        if len(w) >= 6 and w[-3] == w[-4]:          # sparred→spar
            out.append(w[:-3])
    if w.endswith("er") and not w.endswith("ier") and len(w) >= 5:
        out.extend([w[:-1], w[:-2]])
        if len(w) >= 6 and w[-3] == w[-4]:
            out.append(w[:-3])
    if w.endswith("est") and not w.endswith("iest") and len(w) >= 5:
        out.extend([w[:-2], w[:-3]])
        if len(w) >= 6 and w[-4] == w[-5]:
            out.append(w[:-4])
    if w.endswith("ing") and len(w) >= 5:
        out.extend([w[:-3] + "e", w[:-3]])
        if len(w) >= 6 and w[-4] == w[-5]:
            out.append(w[:-4])
    return out


def _find_base(word: str, scored: set[str], full: set[str]) -> str | None:
    """Return the base form if *word* is a regular inflection of a scored word.

    Prefers bases already in the scored set; falls back to short roots (< 4
    chars) that meet the frequency threshold but aren't in the full dictionary
    because it only contains words of 4+ letters.
    """
    candidates = _derive_bases(word)
    # Pass 1 — base already in the scoring dictionary.
    for b in candidates:
        if b in scored and zipf_frequency(b, "en") < MAX_BASE_FREQ:
            return b
    # Pass 2 — short base (e.g. pry, fry, dry) not in the scored set because
    # len < 4, but frequent enough to justify the inflection.
    for b in candidates:
        if len(b) >= 4:
            continue
        bz = zipf_frequency(b, "en")
        if b.isalpha() and bz >= FREQ_THRESHOLD and bz < MAX_BASE_FREQ:
            return b
    return None


def main():
    full = load_word_set(FULL_FILE)
    banned = load_word_set(BAN_FILE)
    keep = load_word_set(KEEP_FILE)

    # --- Pass 1: frequency-based scoring set ---
    common = {
        w for w in full
        if len(w) >= 4 and w.isalpha() and zipf_frequency(w, "en") >= FREQ_THRESHOLD
    }
    common -= banned
    common |= (keep & full)

    # --- Pass 2: inflection boost ---
    boosted = 0
    for w in full:
        if w in common or len(w) < 4 or not w.isalpha() or w in banned:
            continue
        if zipf_frequency(w, "en") < MIN_INFLECTION_FREQ:
            continue
        if _find_base(w, common, full) is not None:
            common.add(w)
            boosted += 1

    with OUT_FILE.open("w", encoding="utf-8") as out:
        for w in sorted(common):
            out.write(w + "\n")

    print(f"Full dictionary:      {len(full)}")
    print(f"Banned:               {len(banned)}")
    print(f"Kept (forced):        {len(keep & full)}")
    print(f"Inflection-boosted:   {boosted}")
    print(f"Scoring dictionary:   {len(common)}  ->  {OUT_FILE}")


if __name__ == "__main__":
    main()
