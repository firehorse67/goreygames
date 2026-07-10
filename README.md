# Michael's Word Games

Free daily word games at **[games.goreythings.com](https://games.goreythings.com)**

## Games

### Sextet
A daily 6-letter word puzzle — like Wordle, but with 6 letters and 6 tries. One new puzzle each day at Melbourne midnight. Players can also play unlimited practice games.

### Target
Find as many words as you can (4 letters or more) using the 9 letters shown, always including the centre letter. Find the 9-letter word for full marks. No plurals, no proper nouns. One new puzzle each day at Melbourne midnight, plus unlimited practice games.

Target uses a **two-tier dictionary**: guesses are accepted against the full ~69k-word dictionary (a real word is never rejected), but the word total, rank thresholds and the Missed list are scored against a smaller frequency-filtered list of familiar words. Valid-but-obscure guesses count as bonus words.

## Repository structure

| File | Purpose |
|------|---------|
| `index.html` | Landing page / game menu |
| `sextet.html` | Sextet game |
| `target.html` | Target game |
| `sextet_answers.txt` | Sextet daily answer list (sorted A–Z for editing; play order is scrambled in-code) |
| `sextet_words.txt` | Full Sextet valid-guess dictionary |
| `target_pool.txt` | **Precomputed** Target puzzles — each line is `WORD CENTER`, sorted A–Z (daily order is scrambled in-code) |
| `target_full.txt` | Full Target accept dictionary (~69k words) |
| `target_common.txt` | Target scoring dictionary (frequency-filtered, ~17.5k words) |
| `target_final.txt` | Source 9-letter word list used to generate `target_pool.txt` |
| `build_sextet_answers.py` | Regenerates `sextet_answers.txt` from `sextet_words.txt` using word frequency |
| `build_sextet_list.py` | Regenerates `sextet_words.txt` from a base word list |
| `build_target_common.py` | Regenerates `target_common.txt` from `target_full.txt` using word frequency |
| `build_target_pool.py` | Regenerates `target_pool.txt` (≥40 findable scoring words per puzzle) |

Optional override files (one word per line, not required to exist): `sextet_ban.txt` / `sextet_keep.txt` for Sextet answers, `target_ban.txt` / `target_keep.txt` for Target scoring and puzzles.

## Regenerating word lists

All build scripts require the [`wordfreq`](https://github.com/rspeer/wordfreq) Python package: `pip install wordfreq`

### Sextet answers
```bash
python build_sextet_answers.py
```

### Target dictionaries
Run after changing `target_full.txt`, `target_final.txt`, ban/keep files, or a frequency threshold (order matters — the pool is built from the common list). Bump the `?v=` cache-busting query strings in `target.html` afterwards.
```bash
python build_target_common.py
python build_target_pool.py
```

## Deployment

Hosted on [Vercel](https://vercel.com). Push to `main` to auto-deploy.

## Analytics

Google Analytics 4 via the goreygames Firebase project. Events tracked:
- `game_start` — daily and practice starts (both games)
- `game_complete` — win/loss with guess count (Sextet); words found, bonus words and total (Target)
- `target_found` — when the 9-letter word is found (Target)

## Copyright

© Michael Gorey. All rights reserved.
