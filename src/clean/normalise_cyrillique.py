#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
normalise_cyrillique.py — Corrige les homoglyphes cyrilliques injectés par
l'OCR dans la bible éwé 1913 (archive.org). ~51 400 occurrences.

Mapping validé sur les mots fréquents (Мами/Мауи/Мажи -> Mawu, Кро -> kpo,
па -> na, момо -> wowo, Еуе -> Eye). Ambiguïtés résolues par corrections
mot-à-mot (ex. ЕПТ -> Rut, titre de livre OCR déformé).

Les codepoints sont écrits en \\uXXXX pour éviter les confusions visuelles
(П cyrillique U+041F vs pi grec U+03A0).

Usage :
  python normalise_cyrillique.py <entree.txt> <sortie.txt> <rapport.txt>
"""

import re
import sys
from collections import Counter

# --- Table caractère : codepoints explicites ------------------------------
# minuscules
_T = {
    0x0430: "a", 0x0431: "b", 0x0432: "v", 0x0433: "r", 0x0434: "g",
    0x0435: "e", 0x0436: "w", 0x0437: "z", 0x0438: "u", 0x0439: "i",
    0x043A: "k", 0x043B: "n", 0x043C: "w", 0x043D: "n", 0x043E: "o",
    0x043F: "n", 0x0440: "p", 0x0441: "c", 0x0442: "m", 0x0443: "y",
    0x0444: "f", 0x0445: "x", 0x0446: "c", 0x0447: "c", 0x0448: "w",
    0x0449: "w", 0x044A: "", 0x044B: "y", 0x044C: "", 0x044D: "e",
    0x044E: "u", 0x044F: "a", 0x0451: "e", 0x0456: "i", 0x0455: "s",
    0x0457: "i", 0x0458: "j", 0x0453: "g", 0x04BB: "h", 0x0454: "e",
    0x0491: "g", 0x0452: "d", 0x045B: "c",
    # majuscules
    0x0410: "A", 0x0411: "B", 0x0412: "V", 0x0413: "R", 0x0414: "G",
    0x0415: "E", 0x0416: "W", 0x0417: "Z", 0x0418: "U", 0x0419: "I",
    0x041A: "K", 0x041B: "N", 0x041C: "M", 0x041D: "N", 0x041E: "O",
    0x041F: "II",  # П = chiffres romains II fusionnés
    0x0420: "P", 0x0421: "C", 0x0422: "M", 0x0423: "Y", 0x0424: "F",
    0x0425: "X", 0x0426: "C", 0x0427: "C", 0x0428: "W", 0x0429: "W",
    0x042B: "Y", 0x042D: "E", 0x042E: "U", 0x042F: "A", 0x0401: "E",
    0x0406: "I", 0x0405: "S", 0x0407: "I", 0x0408: "J", 0x0403: "G",
    0x04BA: "H", 0x0404: "E", 0x0490: "G",
    # grec résiduel éventuel
    0x03A0: "II", 0x03A3: "S",
}
TABLE = str.maketrans({chr(k): v for k, v in _T.items()})

# --- Corrections mot-à-mot (ambiguïtés non résolubles par caractère) ------
CORRECTIONS = [
    (r"\bMayu\b", "Mawu"),        # Мауи
    (r"\bMayuwo\b", "Mawuwo"),
    (r"\bEIIM\b", "Rut"),         # ЕПТ = "Rut" (titre de livre, OCR déformé)
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
        for m in RE_MOT.finditer(s):
            w = m.group()
            if any(ord(c) > 0x024F for c in w):
                residus[w] += 1
        sorties.append(s)

    with open(sortie_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorties))
    with open(rapport_path, "w", encoding="utf-8") as f:
        f.write("mots_residuels\tfrequence\n")
        for w, n in residus.most_common(200):
            f.write(f"{w}\t{n}\n")

    print(f"[OK] {len(sorties)} lignes -> {sortie_path}")
    print(f"[RAPPORT] {sum(residus.values())} mots residuels -> {rapport_path}")
    for w, n in residus.most_common(15):
        print(f"  {w} x{n}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python normalise_cyrillique.py <entree> <sortie> <rapport>", file=sys.stderr)
        sys.exit(1)
    normaliser(sys.argv[1], sys.argv[2], sys.argv[3])
