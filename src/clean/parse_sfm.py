#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_sfm.py — Conversion p.sfm (USFM) -> TSV (livre, chapitre, verset, texte).

Source : BibleCorps/FRA-B-LSG1910-PD-UBS (Segond 1910, domaine public).
Traite les marqueurs standard : \\id, \\h, \\c, \\v.
Nettoie : notes \\x ... \\x*, références \\r, paragraphes \\p, titres \\s, etc.

Usage :
  python parse_sfm.py <dossier_p.sfm> <sortie.tsv>
"""

import argparse
import glob
import os
import re
import sys

# Notes de bas de page : \x + ... \x*  (non-greedy, peut couvrir plusieurs lignes)
RE_XNOTE = re.compile(r"\\x \+.*?\\x\*", re.DOTALL)
# Marqueurs USFM génériques à retirer : \p, \r, \s, \ms1, \mr, \ip, \w...|...\w*, etc.
RE_MARQ = re.compile(r"\\(?:[a-zA-Z0-9]+|\*)(?:\s|$)")
RE_ESPACES = re.compile(r"\s+")

IGNORES = {"id", "ide", "h", "toc1", "toc2", "toc3", "mt1", "imt1", "ie"}


def nettoie_texte(seg: str) -> str:
    """Enlève notes, marqueurs et normalise le texte d'un verset."""
    seg = RE_XNOTE.sub(" ", seg)
    seg = RE_MARQ.sub(" ", seg)
    seg = RE_ESPACES.sub(" ", seg)
    return seg.strip()


def parse_fichier(chemin: str, sortie) -> int:
    livre = os.path.basename(chemin)
    chapitre = 0
    versets = 0
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        for ligne in f:
            ligne = ligne.rstrip("\n")
            if not ligne.strip():
                continue
            if ligne.startswith("\\c "):
                m = re.match(r"\\c\s+(\d+)", ligne)
                chapitre = int(m.group(1)) if m else 0
                continue
            if ligne.startswith("\\v "):
                m = re.match(r"\\v\s+(\d+)\s+(.*)$", ligne, re.DOTALL)
                if not m:
                    continue
                vers = int(m.group(1))
                texte = nettoie_texte(m.group(2))
                if texte:
                    sortie.write(f"{livre}\t{chapitre}\t{vers}\t{texte}\n")
                    versets += 1
                continue
            # Autres lignes : ignorées (titres, notes \r, \p, etc.)
    return versets


def main(dossier: str, sortie_path: str):
    fichiers = sorted(glob.glob(os.path.join(dossier, "*.p.sfm")))
    if not fichiers:
        fichiers = sorted(glob.glob(os.path.join(dossier, "*.sfm")))
    if not fichiers:
        print(f"[ERREUR] Aucun fichier .sfm dans {dossier}", file=sys.stderr)
        sys.exit(1)

    total = 0
    with open(sortie_path, "w", encoding="utf-8") as out:
        out.write("livre\tchapitre\tverset\ttexte\n")
        for f in fichiers:
            n = parse_fichier(f, out)
            total += n
            print(f"  {os.path.basename(f)}: {n} versets")
    print(f"[OK] {total} versets au total -> {sortie_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("sortie")
    args = ap.parse_args()
    main(args.dossier, args.sortie)
