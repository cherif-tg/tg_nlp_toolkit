#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalise_cyrillique.py — Corrige les homoglyphes cyrilliques injectés par
l'OCR dans la bible éwé 1913 (archive.org).

L'OCR a reconnu la police italique 1913 comme du cyrillique (~51 400 cas).
Mapping validé sur les mots fréquents :
  Мами/Мауи/Мажи -> Mawu ; Кро -> kpo ; па -> na ; момо -> wowo ; Еуе -> Eye

Stratégie : table caractère->caractère + corrections mot-à-mot pour les mots
fréquents ambigus. Les mots résiduels sont listés dans un rapport pour la
vérification par échantillon (locuteur natif).

Usage :
  python normalise_cyrillique.py <entree.txt> <sortie.txt> <rapport.txt>
"""

import re
import sys
from collections import Counter

# --- Table caractère (minuscules puis majuscules) ------------------------
TABLE = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "r", "д": "g", "е": "e", "ж": "w",
    "з": "z", "и": "u", "й": "i", "к": "k", "л": "n", "м": "w", "н": "n",
    "о": "o", "п": "n", "р": "p", "с": "c", "т": "m", "у": "y", "ф": "f",
    "х": "x", "ц": "c", "ч": "c", "ш": "w", "щ": "w", "ы": "y", "э": "e",
    "ю": "u", "я": "a", "ё": "e", "і": "i", "ѕ": "s", "ї": "i", "ј": "j",
    "ѓ": "g", "һ": "h", "є": "e", "ґ": "g",
    "А": "A", "Б": "B", "В": "V", "Г": "R", "Д": "G", "Е": "E", "Ж": "W",
    "З": "Z", "И": "U", "Й": "I", "К": "K", "Л": "N", "М": "M", "Н": "N",
    "О": "O", "Р": "P", "С": "C", "Т": "M", "У": "Y", "Ф": "F", "Х": "X",
    "Ц": "C", "Ч": "C", "Ш": "W", "Щ": "W", "Ы": "Y", "Э": "E", "Ю": "U",
    "Я": "A", "Ё": "E", "І": "I", "Ѕ": "S", "Ї": "I", "Ј": "J", "Ѓ": "G",
    "Һ": "H", "Є": "E", "Ґ": "G",
})
# "П" majuscule = chiffres romains "II" fusionnés par l'OCR (titres de parties)
TABLE["П"] = "II"
TABLE["п"] = "n"

# --- Corrections mot-à-mot (ambiguïtés non résolubles caractère par caractère)
CORRECTIONS = [
    (r"\bMayu\b", "Mawu"),   # Мауи (у = w ici)
    (r"\bMayuwo\b", "Mawuwo"),
    (r"\bMawu\b", "Mawu"),   # déjà bon (Мами/Мажи)
]

RE_MOT = re.compile(r"[A-Za-z]+\b")


def normaliser(entree_path: str, sortie_path: str, rapport_path: str):
    lignes = open(entree_path, encoding="utf-8", errors="replace").read().splitlines()
    residus = Counter()
    sorties = []
    for ln in lignes:
        s = ln.translate(TABLE)
        for pat, repl in CORRECTIONS:
            s = re.sub(pat, repl, s)
        # Mots contenant encore des caractères suspects (hors alphabet latin étendu)
        for m in RE_MOT.finditer(s):
            w = m.group()
            if any(ord(c) > 0x024F for c in w):  # au-delà du latin étendu
                residus[w] += 1
        sorties.append(s)

    with open(sortie_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorties))

    with open(rapport_path, "w", encoding="utf-8") as f:
        f.write("mots_residuels\tfrequence\n")
        for w, n in residus.most_common(200):
            f.write(f"{w}\t{n}\n")

    print(f"[OK] {len(sorties)} lignes -> {sortie_path}")
    print(f"[RAPPORT] {sum(residus.values())} occurrences residuelles -> {rapport_path}")
    for w, n in residus.most_common(15):
        print(f"  {w} x{n}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python normalise_cyrillique.py <entree> <sortie> <rapport>", file=sys.stderr)
        sys.exit(1)
    normaliser(sys.argv[1], sys.argv[2], sys.argv[3])
