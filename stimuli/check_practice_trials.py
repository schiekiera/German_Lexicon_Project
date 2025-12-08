#!/usr/bin/env python3
import re
from pathlib import Path

# Pfade anpassen, falls nötig
PRACTICE_PATH = Path(
    "stimuli/practice_trials.js"
)

STIMULUS_PATH = Path(
    "stimuli/stimulus_list.js"
)

# Regex: sucht Zeilen wie   presented_word: 'Haus'
PRESENTED_WORD_RE = re.compile(r"presented_word\s*:\s*'([^']*)'")


def extract_presented_words_from_file(path: Path):
    """Gibt alle gefundenen presented_word-Werte in der Reihenfolge des Auftretens zurück."""
    words = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            m = PRESENTED_WORD_RE.search(line)
            if m:
                words.append(m.group(1))
    return words


def main():
    # 1) Practice-Wörter (kleine Menge)
    practice_words = extract_presented_words_from_file(PRACTICE_PATH)
    practice_set = set(practice_words)

    # 2) Alle einzigartigen Stimulus-Wörter (große Datei, nur Set zum Speichern)
    stimulus_words = set()
    with STIMULUS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            m = PRESENTED_WORD_RE.search(line)
            if m:
                stimulus_words.add(m.group(1))

    # 3) Schnittmenge: welche practice_words kommen auch in stimulus_words vor?
    overlap_in_order = [w for w in practice_words if w in stimulus_words]

    print("Practice-trials, die auch in stimulus_list.js vorkommen:")
    for w in overlap_in_order:
        print(w)


if __name__ == "__main__":
    main()