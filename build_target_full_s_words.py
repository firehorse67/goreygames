#!/usr/bin/env python3
"""One-off repair for target_full.txt: restore real words ending in 'S'.

Investigation found that target_full.txt (the Target *accept* dictionary)
contains ZERO words ending in the letter S -- not just regular plurals, but
every genuine standalone word that happens to end in S too: CHAOS, VIRUS,
ALWAYS, CORPS, TOWARDS, CAMPUS, CLASS, PRESS, and thousands more. Some
earlier build step appears to have stripped every S-ending word outright
instead of only excluding regular plurals/verb-conjugations, so the game
was rejecting countless legitimate everyday words as "Not in dictionary".

This script adds back S-ending words from the `english_words` package's
web2 wordlist (Webster's Second International, a standard reference also
behind most word-game dictionaries), while still excluding regular
inflections (plain plurals, y-to-ies plurals, and sibilant -es forms) of
words already in the dictionary -- so "No plurals" guesses are still
correctly blocked, matching the game's existing design and the runtime
pluralExcluded() check in target.html.

Requires: pip install english_words
"""
from pathlib import Path
from english_words import get_english_words_set
from wordfreq import zipf_frequency

FULL_FILE = Path("target_full.txt")

# web2 (Webster's 1913) is full of archaic scientific/botanical Latin terms
# that would make the "obscure words still allowed" complaint worse, so
# additions require some attestation in modern English rather than being
# accepted purely for existing in web2.
MIN_ZIPF = 0.1

# Words whose "base" (minus the S) coincidentally also exists as a word,
# tripping the regular-inflection check even though they are not plurals
# of that base at all -- forced in regardless of the automatic check below.
FORCE_INCLUDE = {
    # adverbs/prepositions (not plurals of their "-ward"/"-way" cousins)
    "always", "towards", "besides", "afterwards", "backwards", "forwards",
    "nowadays", "indoors", "outdoors", "upstairs", "downstairs", "sideways",
    "overseas", "outwards", "inwards", "upwards", "downwards", "onwards",
    "anyways", "crossways", "northwards", "southwards", "eastwards", "westwards",
    # possessive pronouns, coincidentally "base + s"
    "yours", "theirs", "hers",
    # standalone words whose coincidental "base" is an unrelated archaic/rare word
    "miss", "press", "pass", "status", "species", "bass", "alas", "sans",
    "fuss", "alms", "mumps", "chaos", "loss",
    # plurale tantum nouns -- no singular sense, not "a plural" in the game's sense
    "scissors", "pants", "pliers", "tweezers", "suspenders", "bellows",
    "overalls", "genitals", "briefs", "shorts", "jeans", "trousers", "tongs",
    # academic/field names ending in -ics (grammatically plural, used as singular)
    "physics", "politics", "economics", "ethics", "tactics", "graphics",
    "dynamics", "mechanics", "genetics", "athletics", "logistics", "analytics",
    "aesthetics", "gymnastics", "optics", "metrics", "semantics", "ceramics",
    "acoustics", "obstetrics", "pediatrics", "eugenics", "kinetics",
    "harmonics", "hydraulics", "ballistics", "biometrics", "phonics",
    "civics", "psychics", "tectonics", "theatrics", "phonetics",
    "acrobatics", "statistics", "hysterics",
}

# web2 includes some personal/mythological names that read as ordinary
# words to a frequency check (they appear often in running text) but are
# proper nouns, which the game explicitly excludes.
EXCLUDE_PROPER = {"moses", "hans", "eurystheus", "eumolpus", "wyss"}


def is_regular_inflection(word: str, full: set[str]) -> bool:
    """True if `word` is a plain plural / verb-conjugation of a word already
    in `full` (and so should stay excluded, consistent with "No plurals")."""
    bases = [word[:-1]]                      # dogs -> dog, dimes -> dime
    if word.endswith("ies") and len(word) >= 5:
        bases.append(word[:-3] + "y")        # parties -> party
    if word.endswith("es") and len(word) >= 5:
        bases.append(word[:-2])              # foxes -> fox, watches -> watch
    return any(b in full or (b + "e") in full for b in bases)


def main():
    full = {w.strip().lower() for w in FULL_FILE.read_text().splitlines() if w.strip()}
    before = len(full)

    source = get_english_words_set(["web2"], lower=True)
    candidates = {
        w for w in source
        if w.isalpha() and len(w) >= 4 and w.endswith("s")
        and w not in full and w not in EXCLUDE_PROPER
    }

    added = set()
    for w in candidates:
        if w in FORCE_INCLUDE:
            added.add(w)
            continue
        if zipf_frequency(w, "en") < MIN_ZIPF:
            continue
        if w.endswith("ss"):
            added.add(w)                     # class, press -- never a plural form
            continue
        if not is_regular_inflection(w, full):
            added.add(w)
    added |= (FORCE_INCLUDE - full)

    full |= added

    with FULL_FILE.open("w", encoding="utf-8") as out:
        for w in sorted(full):
            out.write(w + "\n")

    print(f"Before:  {before}")
    print(f"Added:   {len(added)}  (S-ending words that are not plain inflections)")
    print(f"Skipped: {len(candidates) - len(added)}  (regular plurals/verb forms, still excluded)")
    print(f"After:   {len(full)}  -> {FULL_FILE}")


if __name__ == "__main__":
    main()
