#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_bible.py — Extraction complète de la bible éwé 1913 (texte normalisé)
en TSV (livre, chapitre, verset, texte).

Les 66 livres sont délimités par leurs titres (numéros de ligne index 0-based,
localisés manuellement). Les versets sont détectés dans le flux de texte par
leur numéro précédé d'une ponctuation forte (les numéros sont en marge dans le
scan, souvent collés à la fin de la ligne précédente). Un numéro <= au
précédent signale un nouveau chapitre (estimation).

Usage :
  python extract_bible.py <bible_normalisee.txt> <sortie.tsv>
"""

import re
import sys

LIVRES = [
    ("GEN", 274), ("EXO", 8154), ("LEV", 15109), ("NUM", 19806),
    ("DEU", 26283), ("JOS", 32288), ("JDG", 35900), ("RUT", 39431),
    ("1SA", 39881), ("2SA", 44633), ("1KI", 48592), ("2KI", 53588),
    ("1CH", 58594), ("2CH", 62913), ("EZR", 68398), ("NEH", 69902),
    ("EST", 72068), ("JOB", 73157), ("PSA", 77308), ("PRO", 89345),
    ("ECC", 93250), ("SNG", 94497), ("ISA", 95102), ("JER", 103398),
    ("LAM", 111961), ("EZK", 112714), ("DAN", 120340), ("HOS", 122612),
    ("JOL", 123846), ("AMO", 124316), ("OBA", 125294), ("JON", 125416),
    ("MIC", 125807), ("NAM", 126395), ("HAB", 126663), ("ZEP", 127018),
    ("HAG", 127391), ("ZEC", 127627), ("MAL", 129036), ("MAT", 129552),
    ("MRK", 136605), ("LUK", 140438), ("JHN", 147081), ("ACT", 152155),
    ("ROM", 158311), ("1CO", 162213), ("2CO", 165089), ("GAL", 167028),
    ("EPH", 167910), ("PHP", 168933), ("COL", 169730), ("1TH", 170316),
    ("2TH", 170935), ("1TI", 171166), ("2TI", 172101), ("TIT", 172708),
    ("PHM", 173078), ("HEB", 173221), ("JAS", 175371), ("1PE", 176116),
    ("2PE", 176988), ("1JN", 177359), ("2JN", 178276), ("3JN", 178408),
    ("JUD", 178527), ("REV", 178816),
]

RE_PAGE = re.compile(r"^\d+\s*[!.]?$")
RE_REF = re.compile(r"^[a-z?]{1,4}\s*\d{1,3}\s*[,.;:\-–—]\s*\d{1,3}")
RE_ENTETE = re.compile(r"^[A-ZÀ-Ü][A-ZÀ-Ü0-9\'’\- ]{1,40}\.?\s*\d*\.?$")
# Un numéro de verset = 1-3 chiffres précédés d'une ponctuation forte
RE_VERSE = re.compile(r"([.!?:\"\u201d\u2019])\s+(\d{1,3})\s+")
RE_DEBUT_NUM = re.compile(r"^\d{1,3}\s*")
RE_ESPACES = re.compile(r"\s+")
RE_TRAITS = re.compile(r"[\[\]\^\"\u201c\u201d\u2018\u2019]|—{1,3}|\|")


def nettoie_texte(s: str) -> str:
    s = RE_TRAITS.sub(" ", s)
    s = RE_ESPACES.sub(" ", s)
    return s.strip(" .;:,")


def extraire_livre(lignes, debut: int, fin: int, code: str, out, stats: dict):
    # 1) Flux de texte : lignes filtrées, jointes
    morceaux = []
    for ln in lignes[debut + 1:fin]:
        s = ln.strip()
        if not s or RE_PAGE.match(s) or RE_REF.match(s):
            continue
        if RE_ENTETE.match(s) and len(s) <= 45:
            continue
        morceaux.append(s)
    flux = " ".join(morceaux)
    flux = RE_ESPACES.sub(" ", flux)

    # 2) Découpage en versets : numéros précédés de ponctuation forte
    coupes = [m.start(2) for m in RE_VERSE.finditer(flux)]
    segments = []
    debut_seg = 0
    for pos in coupes:
        seg = flux[debut_seg:pos].strip()
        if seg:
            segments.append(seg)
        debut_seg = pos
    reste = flux[debut_seg:].strip()
    if reste:
        segments.append(reste)

    # 3) Chaque segment commence par "N texte" -> verset N
    n_versets = 0
    n_chapitres = 0
    dernier = 0
    for seg in segments:
        m = re.match(r"^(\d{1,3})\s+(.*)$", seg)
        if not m:
            continue
        num = int(m.group(1))
        texte = nettoie_texte(m.group(2))
        if not texte:
            continue
        if num <= dernier:
            n_chapitres += 1
        dernier = num
        out.write(f"{code}\t{n_chapitres}\t{num}\t{texte}\n")
        n_versets += 1
    stats[code] = (n_chapitres, n_versets)


def main(entree_path: str, sortie_path: str):
    lignes = open(entree_path, encoding="utf-8").read().splitlines()
    stats = {}
    total = 0
    with open(sortie_path, "w", encoding="utf-8") as out:
        out.write("livre\tchapitre\tverset\ttexte\n")
        for i, (code, pos) in enumerate(LIVRES):
            fin = LIVRES[i + 1][1] if i + 1 < len(LIVRES) else len(lignes)
            extraire_livre(lignes, pos, fin, code, out, stats)
    for code, (ch, vs) in stats.items():
        total += vs
        print(f"  {code}: {ch} chap, {vs} vers")
    print(f"[OK] {total} versets -> {sortie_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_bible.py <bible_normalisee.txt> <sortie.tsv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
