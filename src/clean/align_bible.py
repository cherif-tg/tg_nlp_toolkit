#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
align_bible.py — Alignement verset à verset bible éwé 1913 <-> Segond 1910
(programmation dynamique à bande limitée sur les numéros de versets).

Le chapitre estimé de l'OCR éwé n'est pas fiable (resets parasites) : on
aligne donc les SÉQUENCES de numéros de versets par livre avec un DP à bande
(Needleman-Wunsch, match +2 / mismatch -1 / gap -1), ce qui absorbe les
numéros avalés, les parasites et les versets manquants.

Sorties :
  <sortie>.tsv          : paires (livre;chapitre;verset;fr;ewe;confiance)
  <sortie>.rapport.txt  : stats + outliers

Usage :
  python align_bible.py <segond.tsv> <ewe.tsv> <sortie.tsv>
"""

import re
import sys

CODES = ["GEN","EXO","LEV","NUM","DEU","JOS","JDG","RUT","1SA","2SA","1KI","2KI",
         "1CH","2CH","EZR","NEH","EST","JOB","PSA","PRO","ECC","SNG","ISA","JER",
         "LAM","EZK","DAN","HOS","JOL","AMO","OBA","JON","MIC","NAM","HAB","ZEP",
         "HAG","ZEC","MAL","MAT","MRK","LUK","JHN","ACT","ROM","1CO","2CO","GAL",
         "EPH","PHP","COL","1TH","2TH","1TI","2TI","TIT","PHM","HEB","JAS","1PE",
         "2PE","1JN","2JN","3JN","JUD","REV"]

RE_CODE = re.compile(r"-(\d+)-([A-Z0-9]+)\.")
BANDE = 250  # décalage max autorisé entre les deux séquences


def lire_segond(path):
    """livre -> [(chap, ver, texte)] ordre canonique"""
    d = {}
    with open(path, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            m = RE_CODE.search(p[0])
            code = m.group(2) if m else p[0]
            d.setdefault(code, []).append((int(p[1]), int(p[2]), p[3]))
    return d


def lire_ewe(path):
    """livre -> [(chap_est, ver, texte)] ordre du texte"""
    d = {}
    with open(path, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            d.setdefault(p[0], []).append((int(p[1]), int(p[2]), p[3]))
    return d


def dp_align(ewe_nums, seg_nums, B=BANDE):
    """Retourne la liste des paires (i_ewe, j_seg) alignées (DP à bande, dicts)."""
    n, m = len(ewe_nums), len(seg_nums)
    NEG = -10 ** 9
    dp = [{} for _ in range(n + 1)]
    tb = [{} for _ in range(n + 1)]
    for i in range(n, -1, -1):
        jmin = max(0, i - B)
        jmax = min(m, i + B)
        for j in range(jmax, jmin - 1, -1):  # décroissant : dp[i][j+1] doit être connu
            if i == n or j == m:
                dp[i][j] = 0
                continue
            d = dp[i + 1].get(j + 1, NEG) + (2 if ewe_nums[i] == seg_nums[j] else -5)
            h = dp[i + 1].get(j, NEG) - 1
            g = dp[i].get(j + 1, NEG) - 1
            best = max(d, h, g)
            dp[i][j] = best
            tb[i][j] = 1 if best == d else (2 if best == h else 3)

    paires = []
    i = j = 0
    while i < n and j < m:
        d = tb[i].get(j, 3)
        if d == 1:
            paires.append((i, j))
            i += 1
            j += 1
        elif d == 2:
            i += 1
        else:
            j += 1
    return paires


def main(seg_path, ewe_path, sortie_path):
    seg = lire_segond(seg_path)
    ewe = lire_ewe(ewe_path)

    total_paires = 0
    total_conf = 0
    total_ewe = sum(len(v) for v in ewe.values())
    outliers = []
    ratios = []

    with open(sortie_path, "w", encoding="utf-8") as out:
        out.write("livre\tchapitre\tverset\tfr\tewe\tconfiance\n")
        for code in CODES:
            segc = seg.get(code, [])
            ewec = ewe.get(code, [])
            if not segc or not ewec:
                continue
            paires = dp_align([v[1] for v in ewec], [v[1] for v in segc])
            for i, j in paires:
                chap, ver, txt = ewec[i]
                schap, sver, sfr = segc[j]
                conf = "ok" if ver == sver else "decale"
                ratio = len(txt) / max(len(sfr), 1)
                ratios.append(ratio)
                out.write(f"{code}\t{schap}\t{sver}\t{sfr}\t{txt}\t{conf}\n")
                total_paires += 1
                if conf == "ok":
                    total_conf += 1
                if ratio < 0.3 or ratio > 4.0:
                    outliers.append((code, schap, sver, round(ratio, 2), sfr[:50], txt[:50]))

    rapport_path = sortie_path.replace(".tsv", ".rapport.txt")
    with open(rapport_path, "w", encoding="utf-8") as r:
        r.write(f"versets ewe: {total_ewe}\n")
        r.write(f"paires alignees: {total_paires}\n")
        r.write(f"  dont numeros identiques (conf ok): {total_conf} ({100*total_conf/max(total_paires,1):.1f}%)\n")
        r.write(f"  dont numeros decales (conf decale): {total_paires-total_conf}\n")
        r.write(f"ratio moyen |ewe|/|fr|: {sum(ratios)/max(len(ratios),1):.2f}\n")
        r.write(f"ratio median: {sorted(ratios)[len(ratios)//2] if ratios else 0:.2f}\n")
        r.write(f"outliers (ratio < 0.3 ou > 4.0): {len(outliers)}\n")
        for x in outliers[:40]:
            r.write(f"  {x[0]} {x[1]}:{x[2]} ratio={x[3]} | FR: {x[4]} | EW: {x[5]}\n")

    print(f"[OK] {total_paires} paires (dont {total_conf} numeros identiques) / {total_ewe} versets ewe")
    print(f"[RAPPORT] ratio moyen {sum(ratios)/max(len(ratios),1):.2f} -> {rapport_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python align_bible.py <segond.tsv> <ewe.tsv> <sortie.tsv>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
