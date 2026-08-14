#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_corpus.py v2 — Nettoyage fin du corpus aligné bible éwé <-> Segond.

v2 (calibré sur l'échantillon de vérification du locuteur natif) :
- Nettoyage renforcé : guillemets allemands, caractères non-latins résiduels,
  abréviations supplémentaires (Mem, RE...), fragments "> ,28."
- Seuils de ratio resserrés (ok : 0.6 <= ratio <= 1.8) — le locuteur a montré
  que les versets fusionnés (ratio median 2.6) sont la principale source d'erreur.

Sortie : TSV (livre;chapitre;verset;fr;ewe;ratio;flag)
  flag = ok | a-verifier

Usage :
  python clean_corpus.py <alignes.tsv> <sortie.tsv>
"""

import re
import sys

ABREV = ("Gen|Ex|Lev|Num|Deu|Jos|Jdg|Rut|Sam|Ki|Chr|Ezr|Neh|Est|Job|Psa|Ps|Pro|"
         "Ecc|Sng|Isa|Jer|Lam|Ezk|Dan|Hos|Jol|Amo|Oba|Jon|Mic|Nam|Hab|Zep|Hag|"
         "Zec|Mal|Mat|Mrk|Luk|Jhn|Act|Rom|Cor|Gal|Eph|Php|Col|Thes|Th|Tim|Ti|"
         "Tit|Phm|Heb|Jas|Pet|Pe|Jn|Jud|Rev|Nyad|Tes|Mo|Yes|Yer|Hez|Hoz|Yoe|"
         "Zak|Mal|Abd|Yon|Nah|Hab|Sof|Agg|Zah|Mih|Mic|Mem|RE|Ru")
RE_REF = re.compile(
    r"\b(?:[1-3]\s*)?(?:" + ABREV + r")\.?\s*,?\s*\d{1,3}\s*[,.:]\s*\d{1,3}"
    r"(?:\s*[-–—;]\s*\d{1,3}\s*[,.]?\s*\d{0,3})?"
)
RE_REF2 = re.compile(
    r"\b[a-z]\s+(?:" + ABREV + r")\.?\s*(?:I{1,3}|IV|V|VI|[1-3])\b"
)
RE_DEBUT_NUM = re.compile(r"^\d{1,3}\s*")
RE_ESPACES = re.compile(r"\s+")
RE_PONCT = re.compile(r"[,;:]$")
# Caractères résiduels à supprimer : guillemets allemands, symboles isolés
RE_SYMB = re.compile(r"[„“”‘’\"°^<>~`=+*_#@$%&]")
# Fragments de notes : "> ,28." ou ",28." après symbole
RE_FRAG = re.compile(r">\s*,?\s*\d{1,3}\.?")

RATIO_MAX = 1.8   # v2 : resserré (locuteur : ok median 1.01, corriger median 2.59)
RATIO_MIN = 0.6


def nettoie_ewe(txt: str) -> str:
    txt = RE_DEBUT_NUM.sub("", txt)
    txt = RE_REF.sub(" ", txt)
    txt = RE_REF2.sub(" ", txt)
    txt = RE_FRAG.sub(" ", txt)
    txt = RE_SYMB.sub(" ", txt)
    # lettres non-latines résiduelles (hors latin étendu)
    txt = "".join(c if ord(c) <= 0x024F or c.isspace() else " " for c in txt)
    txt = RE_ESPACES.sub(" ", txt)
    txt = RE_PONCT.sub("", txt)
    return txt.strip()


def main(entree_path: str, sortie_path: str):
    total = ok = a_verifier = 0
    with open(entree_path, encoding="utf-8") as f, \
         open(sortie_path, "w", encoding="utf-8") as out:
        out.write("livre\tchapitre\tverset\tfr\tewe\tratio\tflag\n")
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 6:
                continue
            code, chap, ver, fr, ewe = p[0], p[1], p[2], p[3], p[4]
            ewe = nettoie_ewe(ewe)
            if not ewe:
                continue
            ratio = len(ewe) / max(len(fr), 1)
            flag = "ok" if RATIO_MIN <= ratio <= RATIO_MAX else "a-verifier"
            total += 1
            if flag == "ok":
                ok += 1
            else:
                a_verifier += 1
            out.write(f"{code}\t{chap}\t{ver}\t{fr}\t{ewe}\t{ratio:.2f}\t{flag}\n")

    print(f"[OK] {total} paires ({ok} ok, {a_verifier} a-verifier) -> {sortie_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_corpus.py <alignes.tsv> <sortie.tsv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
