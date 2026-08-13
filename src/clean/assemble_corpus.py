#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assemble_corpus.py — Assemble le corpus parallèle v0.1 (FR<->Éwé).

- Noyau publiable : paires "ok" (ratio de longueur normal)
- Candidates : paires "a-verifier" (versets fusionnés par l'OCR), conservées à part
- Split 80/10/10 stratifié par livre (seed fixe pour reproductibilité)

Sorties (dossier v0.1/) :
  train.tsv, dev.tsv, test.tsv   (livre;chapitre;verset;fr;ewe)
  candidates-a-verifier.tsv
  STATS.md

Usage :
  python assemble_corpus.py <corpus_clean.tsv> <dossier_sortie>
"""

import os
import random
import sys

SEED = 42
RATIO_TRAIN = 0.8


def main(corpus_path: str, dossier: str):
    random.seed(SEED)
    os.makedirs(dossier, exist_ok=True)

    ok_par_livre = {}
    a_verifier = []
    with open(corpus_path, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            code, chap, ver, fr, ewe = p[0], p[1], p[2], p[3], p[4]
            flag = p[6]
            if flag == "ok":
                ok_par_livre.setdefault(code, []).append((code, chap, ver, fr, ewe))
            else:
                a_verifier.append((code, chap, ver, fr, ewe))

    # Split stratifié par livre
    train, dev, test = [], [], []
    for code, rows in sorted(ok_par_livre.items()):
        random.shuffle(rows)
        n = len(rows)
        n_test = max(1, round(n * (1 - RATIO_TRAIN) / 2))
        n_dev = max(1, round(n * (1 - RATIO_TRAIN) / 2))
        if n <= 3:
            train.extend(rows)  # livres minuscules : tout en train
            continue
        test.extend(rows[:n_test])
        dev.extend(rows[n_test:n_test + n_dev])
        train.extend(rows[n_test + n_dev:])

    def ecrire(rows, nom):
        path = os.path.join(dossier, nom)
        with open(path, "w", encoding="utf-8") as f:
            f.write("livre\tchapitre\tverset\tfr\tewe\n")
            for code, chap, ver, fr, ewe in rows:
                f.write(f"{code}\t{chap}\t{ver}\t{fr}\t{ewe}\n")
        return path

    p_train = ecrire(train, "train.tsv")
    p_dev = ecrire(dev, "dev.tsv")
    p_test = ecrire(test, "test.tsv")
    p_cand = ecrire(a_verifier, "candidates-a-verifier.tsv")

    with open(os.path.join(dossier, "STATS.md"), "w", encoding="utf-8") as f:
        f.write("# Corpus v0.1 — stats\n\n")
        f.write(f"- paires ok : {len(train) + len(dev) + len(test)}\n")
        f.write(f"  - train : {len(train)}\n")
        f.write(f"  - dev   : {len(dev)}\n")
        f.write(f"  - test  : {len(test)}\n")
        f.write(f"- candidates a-verifier : {len(a_verifier)}\n")
        f.write(f"- livres couverts : {len(ok_par_livre)}\n")
        f.write(f"- seed : {SEED}\n")

    print(f"[OK] train={len(train)} dev={len(dev)} test={len(test)} "
          f"candidates={len(a_verifier)} livres={len(ok_par_livre)}")
    print(f"  -> {p_train}")
    print(f"  -> {p_dev}")
    print(f"  -> {p_test}")
    print(f"  -> {p_cand}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python assemble_corpus.py <corpus_clean.tsv> <dossier_sortie>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
