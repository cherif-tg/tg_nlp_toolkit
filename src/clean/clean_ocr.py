#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_ocr.py — Nettoyage de base du texte OCR (bible éwé 1913, archive.org).

Pipeline v0.1 (exploratoire) :
  1. Suppression des lignes de bruit (références croisées, pages, orphelins).
  2. Dé-hyphenation des mots coupés en fin de ligne (anyi- / gba -> anyigba).
  3. Fusion des lignes d'un même verset + détection des numéros de versets.
  4. Sortie TSV : livre, chapitre, verset, texte brut (diacritiques NON restaurés).

Usage :
  python clean_ocr.py <entree.txt> <sortie.tsv> [--debut N --fin M]

Note : ce script ne fait AUCUNE restauration de diacritiques ni correction
linguistique — c'est un nettoyage mécanique. La vérification linguistique
par locuteur natif reste obligatoire (échantillonnage).
"""

import argparse
import re
import sys


# --- Bruit typique de ce scan -------------------------------------------
# Références croisées type "e 18, 7." / "h1, 10-14." / "? 90, 28."
RE_REF = re.compile(r"^[a-z?]{1,3}\s*\d{1,3},\s*\d{1,3}(\.|-|–)?$")
# Lignes qui sont juste des numéros ou ponctuation
RE_NUM_SEUL = re.compile(r"^[\d\s\.,;:!?()\-–—]+$")
# Marqueurs de pages/titres répétitifs
RE_PAGE = re.compile(r"^(\s*\d+\s*)$")

# Dé-hyphenation : mot coupé en fin de ligne (traite aussi "w�-" etc.)
RE_HYPHEN_EOL = re.compile(r"([A-Za-zƐƆŊɖɖ̶ɛɔŋɸʋɡ])\s*-\s*$")

# Numéro de verset : 1 à 3 chiffres (parfois collé au texte précédent)
RE_VERSE = re.compile(r"(?<!\d)(\d{1,3})(?!\d)")


def est_bruit(ligne: str) -> bool:
    """Détecte les lignes qui ne sont pas du texte biblique."""
    s = ligne.strip()
    if not s:
        return True
    if RE_REF.match(s) or RE_NUM_SEUL.match(s) or RE_PAGE.match(s):
        return True
    # Ligne avec plus de 40% de caractères de remplacement
    if s.count("\ufffd") / max(len(s), 1) > 0.4:
        return True
    return False


def dehyphen(texte: str) -> str:
    """Rejoint les mots coupés en fin de ligne."""
    return RE_HYPHEN_EOL.sub(r"\1", texte)


def nettoyer(entree: str, sortie: str, debut: int = None, fin: int = None):
    with open(entree, "r", encoding="utf-8", errors="replace") as f:
        lignes = f.readlines()

    if debut is not None or fin is not None:
        lignes = lignes[debut - 1:fin] if debut else lignes[:fin]

    # 1) Filtrage du bruit
    propres = []
    for ln in lignes:
        s = ln.strip()
        if est_bruit(s):
            continue
        s = s.replace("\ufffd", "").strip()
        s = re.sub(r"\s+", " ", s)
        propres.append(s)

    # 2) Dé-hyphenation + fusion en un flux
    flux = " ".join(propres)
    flux = dehyphen(flux)
    flux = re.sub(r"\s+", " ", flux)

    # 3) Découpage en versets : un numéro (1-3 chiffres) précédé de
    #    ponctuation forte (incl. guillemets) marque un nouveau verset.
    #    Ex. : 'anyigba." 2 Ke anyigba' -> le '2' démarre le verset suivant.
    RE_DEBUT_VERSE = re.compile(r"([.!?:\"\u201d\u2019\u201c])\s+(\d{1,3})\s+")
    coupes = [m.start(2) for m in RE_DEBUT_VERSE.finditer(flux)]
    versets = []
    debut = 0
    for pos in coupes:
        seg = flux[debut:pos].strip()
        if seg:
            versets.append(seg)
        debut = pos
    reste = flux[debut:].strip()
    if reste:
        versets.append(reste)

    # 4) Écriture TSV (livre/chapitre inconnus à ce stade -> GEN 1 provisoire)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("livre\tchapitre\tverset\ttexte\n")
        for i, v in enumerate(versets, start=1):
            f.write(f"GEN\t1\t{i}\t{v}\n")

    print(f"[OK] {len(versets)} versets extraits -> {sortie}")
    for i, v in enumerate(versets[:12], start=1):
        print(f"  Gen 1:{i:>3}  {v[:90]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("entree")
    ap.add_argument("sortie")
    ap.add_argument("--debut", type=int, default=None)
    ap.add_argument("--fin", type=int, default=None)
    args = ap.parse_args()
    try:
        nettoyer(args.entree, args.sortie, args.debut, args.fin)
    except Exception as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        sys.exit(1)
