#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_riebstein.py — Nettoyage v2 du lexique Riebstein.

Problèmes détectés (14 % des 8 575 entrées) :
1. Entrées voisines collées dans le champ traduction_ewe (l'OCR du
   dictionnaire enchaîne l'entrée suivante : « abondance → agbososo.
   abondant a sogbo… »)
2. Coupures de ligne OCR dans les mots composés (« ta- nana » → « ta-nana »)
3. Espacements multiples hérités de la mise en page en colonnes

Traitements :
- Couper le champ traduction au premier motif d'« entrée suivante »
  (mot + double espace + nature grammaticale courte)
- Couper au premier « . » suivi d'un mot en minuscule (fin de traduction)
- Réparer les césures (« mot- espace » → « mot- »)
- Normaliser les espaces et la ponctuation de fin
- Retirer les entrées dont la traduction devient vide

Usage : python scripts/clean_riebstein.py
Sortie : data/processed/riebstein-lexique-v2.tsv
"""

import io
import re

ENTREE = "data/processed/riebstein-lexique-v1.tsv"
SORTIE = "data/processed/riebstein-lexique-v2.tsv"

# Motif A : début d'une entrée suivante « mot    nature    traduction »
RE_ENTREE_SUIVANTE = re.compile(
    r"\s{2,}[A-Za-zÀ-ÖØ-öø-ÿ]+\s{2,}[aîvmtfprn]{1,3}\s{2,}"
)
# Motif B : nature entre parenthèses « (a) », « (î) »
RE_NATURE_PAREN = re.compile(r"\s*\([aîvmtfprn]{1,3}\)\s*")
# Motif C : point suivi d'un mot en minuscule (début d'une nouvelle entrée)
RE_POINT_SUITE = re.compile(r"\.\s+[a-zà-ÿ]")
# Motif D : césure OCR (tiret suivi d'espaces)
RE_CESURE = re.compile(r"([A-Za-zÀ-ÖØ-öø-ÿ])-(\s+)")
RE_ESPACES = re.compile(r"\s{2,}")
RE_PONCT_FIN = re.compile(r"[\s,;:.]+$")
RE_DEBUT = re.compile(r"^[\s,;:.]+")


def nettoyer_trad(txt: str) -> str:
    # 1. couper au motif A (entrée suivante : mot + 2esp + nature + 2esp)
    m = RE_ENTREE_SUIVANTE.search(txt)
    if m:
        txt = txt[: m.start()]
    # 2. couper au motif B (nature entre parenthèses)
    m = RE_NATURE_PAREN.search(txt)
    if m:
        txt = txt[: m.start()]
    # 3. couper au premier point suivi d'un mot en minuscule
    m = RE_POINT_SUITE.search(txt)
    if m:
        txt = txt[: m.start()]
    # 4. réparer les césures OCR : « ta- nana » → « ta-nana »
    txt = RE_CESURE.sub(lambda mm: mm.group(1) + "-", txt)
    # 5. normaliser espaces multiples
    txt = RE_ESPACES.sub(" ", txt)
    # 6. ponctuation de début/fin parasite
    txt = RE_PONCT_FIN.sub("", txt)
    txt = RE_DEBUT.sub("", txt)
    return txt.strip()


def main():
    total = 0
    modifies = 0
    vides = 0
    gardees = []
    with io.open(ENTREE, encoding="utf-8") as f:
        header = next(f)
        for ln in f:
            p = ln.rstrip("\n").split(";")
            if len(p) < 5:
                continue
            section, entree, nature, sous, trad = p[0], p[1], p[2], p[3], p[4]
            total += 1
            avant = trad
            trad = nettoyer_trad(trad)
            if trad != avant.strip():
                modifies += 1
            if not trad:
                vides += 1
                continue
            gardees.append((section, entree, nature, sous, trad))

    with io.open(SORTIE, "w", encoding="utf-8") as f:
        f.write(header)
        for section, entree, nature, sous, trad in gardees:
            f.write(f"{section};{entree};{nature};{sous};{trad}\n")

    print(f"Entrées lues       : {total}")
    print(f"Traductions modifiées : {modifies} ({100*modifies/total:.0f} %)")
    print(f"Entrées vidées/retirées : {vides}")
    print(f"Entrées conservées : {len(gardees)}")
    print(f"Sortie : {SORTIE}")

    print("\n=== Exemples avant → après ===")
    exemples = [
        "agbososo. en-   le  agbososo  me,  fû. abondant   a    sogbo,  bo,  bowâ\\vâ,  tsekplanya.",
        "nunonlo be. tomber  dans  P-    dze  le  bu  ame  îe  nku  dzi,  de ame.",
        "ya lé, ya tsi, yaîoîo nu lé. abattu    a    dzimalé,  gblodo,  deîotoe.",
        "kplu, akogoe, konko. cou  —  cou",
        "ta- nana.  candidature    î  dodzidzi.",
    ]
    for ex in exemples:
        print(f"  AVANT: {ex[:70]}")
        print(f"  APRÈS: {nettoyer_trad(ex)[:70]}")
        print()


if __name__ == "__main__":
    main()
