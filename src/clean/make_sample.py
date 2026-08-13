#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_sample.py — Échantillon de vérification pour le locuteur natif.

Sélectionne 100 paires du corpus nettoyé :
  - ~70 paires "ok" : au moins 1 par livre, puis aléatoire stratifiée
  - ~30 paires "a-verifier" : aléatoires (cas douteux à trancher)

Sorties :
  <dossier>/echantillon-verification-100.csv   (ID;ref;fr;ewe;statut)
  <dossier>/echantillon-verification-100.md    (aperçu lisible)

Usage :
  python make_sample.py <corpus_clean.tsv> <dossier_sortie>
"""

import csv
import random
import sys

N_OK = 70
N_AV = 30
SEED = 42


def main(corpus_path: str, dossier: str):
    random.seed(SEED)
    ok_by_livre = {}
    a_verifier = []
    with open(corpus_path, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            code, chap, ver, fr, ewe, ratio, flag = p[0], p[1], p[2], p[3], p[4], p[5], p[6]
            ref = f"{code} {chap}:{ver}"
            if flag == "ok":
                ok_by_livre.setdefault(code, []).append((ref, fr, ewe, ratio))
            else:
                a_verifier.append((ref, fr, ewe, ratio))

    # 1) au moins 1 "ok" par livre (66 livres -> 66 paires)
    selection = []
    for code in sorted(ok_by_livre):
        selection.append(random.choice(ok_by_livre[code]))
    # 2) compléter jusqu'à N_OK
    restants = [x for code in ok_by_livre for x in ok_by_livre[code] if x not in selection]
    random.shuffle(restants)
    selection += restants[: max(0, N_OK - len(selection))]
    # 3) a-verifier
    random.shuffle(a_verifier)
    selection += a_verifier[:N_AV]

    random.shuffle(selection)
    rows = [(i + 1, ref, fr, ewe, "") for i, (ref, fr, ewe, r) in enumerate(selection)]

    csv_path = f"{dossier}/echantillon-verification-100.csv"
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["ID", "reference", "francais", "ewe", "statut"])
        w.writerows(rows)

    md_path = f"{dossier}/echantillon-verification-100.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Échantillon de vérification — 100 paires FR↔Éwé\n\n")
        f.write("Instructions : pour chaque paire, vérifier la traduction éwé "
                "(orthographe, diacritiques ɛ ɔ ŋ ƒ, sens). Mettre le statut : "
                "`ok`, `corriger` (avec la correction), ou `a-rejeter`.\n\n")
        f.write("| # | Réf | Français | Éwé | Statut |\n")
        f.write("|---|-----|----------|-----|--------|\n")
        for i, ref, fr, ewe, _ in rows:
            fr_c = fr.replace("|", "/")[:90]
            ew_c = ewe.replace("|", "/")[:90]
            f.write(f"| {i} | {ref} | {fr_c} | {ew_c} |  |\n")

    print(f"[OK] {len(rows)} paires -> {csv_path}")
    print(f"[OK] aperçu lisible -> {md_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python make_sample.py <corpus_clean.tsv> <dossier_sortie>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
