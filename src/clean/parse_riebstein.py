#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_riebstein.py — Extraction des entrées FR->EWE du Vocabulaire de
Riebstein (1926, vol. 2 français-éwé, archive.org, domaine public).

Structure du scan :
  - Lignes "A", "B", ... = sections alphabétiques
  - Entrée principale : "abaissement    m  bobodeanyi."
      -> mot FR, NATURE grammaticale (signal fiable), traductions éwé
  - Sous-entrée      : "-des  prix      asidzidede,  nudzidede."
      -> complément FR puis traductions (split au plus grand run d'espaces)
  - Lignes de continuation (traductions coupées) fusionnées à l'entrée en cours

Sortie TSV (séparateur ;) : section;entree;nature;sous_entree;traduction_ewe

Usage :
  python parse_riebstein.py <entree.txt> <sortie.tsv>
"""

import argparse
import re
import sys

NATURES = {
    "m", "f", "vt", "v", "adj", "adv", "pr", "conj", "interj", "pl",
    "n", "pron", "prép", "prep", "part", "loc",
}
RE_SECTION = re.compile(r"^[A-Z]$")
RE_NUM_PAGE = re.compile(r"^\d+$")
RE_ENTREE_TETE = re.compile(r"^([a-zàâäéèêëîïôöùûüÿçœ'’][^.]*?)\s{2,}(.+)$")
RE_SOUS_TETE = re.compile(r"^-\s*(.+)$")
RE_ESPACES = re.compile(r"\s+")


def nettoie(s: str) -> str:
    return RE_ESPACES.sub(" ", s).strip()


def plus_grand_run(ligne: str):
    """Coupe au plus grand run d'espaces (>=2). Retourne (avant, apres) ou None."""
    runs = [(m.start(), m.end()) for m in re.finditer(r" {2,}", ligne)]
    if not runs:
        return None
    (a, b) = max(runs, key=lambda r: r[1] - r[0])
    return ligne[:a].strip(), ligne[b:].strip()


def est_nature(mot: str) -> bool:
    return mot.strip(".") in NATURES


def parse(entree_path: str, sortie_path: str):
    lignes = open(entree_path, encoding="utf-8").read().splitlines()

    debut = 0
    for i, ln in enumerate(lignes):
        if RE_SECTION.match(ln.strip()):
            debut = i
            break

    section, entree, nature, sous, trad = "", "", "", "", ""
    n_entrees = n_sous = 0

    with open(sortie_path, "w", encoding="utf-8") as out:
        out.write("section;entree;nature;sous_entree;traduction_ewe\n")

        for ln in lignes[debut:]:
            s = ln.strip()
            if not s or RE_NUM_PAGE.match(s):
                continue
            if RE_SECTION.match(s):
                section = s
                continue

            # --- Sous-entrée : tiret initial -------------------------------
            m = RE_SOUS_TETE.match(s)
            if m:
                coupure = plus_grand_run(m.group(1))
                if coupure:
                    if trad:
                        out.write(f"{section};{entree};{nature};{sous};{trad}\n")
                        n_entrees += 1
                    sous = nettoie(coupure[0])
                    trad = nettoie(coupure[1])
                    entree, nature = "", ""
                    n_sous += 1
                continue

            # --- Entrée principale : tête + nature grammaticale ------------
            m = RE_ENTREE_TETE.match(s)
            if m:
                tete = nettoie(m.group(1))
                reste = nettoie(m.group(2))
                parts = reste.split(" ", 1)
                if est_nature(parts[0]):
                    if trad:
                        out.write(f"{section};{entree};{nature};{sous};{trad}\n")
                        n_entrees += 1
                    entree, nature = tete, parts[0].strip(".")
                    trad = nettoie(parts[1]) if len(parts) > 1 else ""
                    sous = ""
                    continue

            # --- Continuation : fusion avec la traduction en cours ---------
            if trad:
                trad = trad + " " + s

        if trad:
            out.write(f"{section};{entree};{nature};{sous};{trad}\n")
            n_entrees += 1

    print(f"[OK] {n_entrees} entrees (dont {n_sous} sous-entrees) -> {sortie_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("entree")
    ap.add_argument("sortie")
    args = ap.parse_args()
    try:
        parse(args.entree, args.sortie)
    except Exception as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        sys.exit(1)
