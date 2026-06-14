# Michael's Word Games

Free daily word games at **[games.goreythings.com](https://games.goreythings.com)**

## Games

### Sextet
A daily 6-letter word puzzle — like Wordle, but with 6 letters and 6 tries. One new puzzle each day at Melbourne midnight. Players can also play unlimited practice games.

### Target
Find as many words as you can (4 letters or more) using the 9 letters shown, always including the centre letter. Find the 9-letter word for full marks. No plurals, no proper nouns.

## Repository structure

| File | Purpose |
|------|---------|
| `index.html` | Landing page / game menu |
| `sextet.html` | Sextet game |
| `target.html` | Target game |
| `sextet_answers.txt` | Sextet daily answer list (sorted A–Z for editing; play order is scrambled in-code) |
| `sextet_words.txt` | Full Sextet valid-guess dictionary |
| `target_pool.txt` | **Precomputed** target puzzles — each line is `WORD CENTER` (regenerate if word lists change) |
| `target_full.txt` | Full Target dictionary (~69k words) |
| `target_final.txt` | Source 9-letter word list used to generate `target_pool.txt` |
| `build_sextet_answers.py` | Regenerates `sextet_answers.txt` from `sextet_words.txt` using word frequency |
| `build_sextet_list.py` | Regenerates `sextet_words.txt` from a base word list |

## Regenerating word lists

### Sextet answers
Requires the [`wordfreq`](https://github.com/rspeer/wordfreq) Python package:
```bash
pip install wordfreq
python build_sextet_answers.py
```

### Target pool
Run after changing `target_final.txt` or `target_full.txt`:
```bash
node build_target_pool.js
```
*(See `target_pool.txt` comments for the filter logic — minimum 40 valid words per puzzle.)*

## Deployment

Hosted on [Vercel](https://vercel.com). Push to `main` to auto-deploy.

## Analytics

Google Analytics 4 via the goreygames Firebase project. Events tracked:
- `game_start` — daily and practice starts (Sextet); new game (Target)
- `game_complete` — win/loss with guess count (Sextet); words found vs total (Target)
- `target_found` — when the 9-letter word is found (Target)

## Copyright

© Michael Gorey. All rights reserved.
