#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verif_riebstein.py — Piste 2 : le vocabulaire Riebstein est-il incorporé
dans le corpus v0.2 ?

Méthode :
- Lexique Riebstein (8 575 entrées FR→ÉWÉ, 1926) : on extrait le mot FR
  (colonne « entree ») et les mots ÉWÉ (colonne « traduction_ewe »).
- Corpus v0.2 (16 050 paires) : on construit le vocabulaire (types uniques)
  côté FR et côté ÉWÉ.
- On mesure la COUVERTURE : quelle part du vocabulaire Riebstein apparaît
  au moins une fois dans le corpus, dans chaque langue.

Sortie : data/processed/v0.2/COUVERTURE-RIEBSTEIN.md

Usage : python scripts/verif_riebstein.py
"""

import io
import re
import statistics
from collections import Counter

RIEBSTEIN = "data/processed/riebstein-lexique-v2.tsv"
SPLITS = [
    "data/processed/v0.2/train.tsv",
    "data/processed/v0.2/dev.tsv",
    "data/processed/v0.2/test.tsv",
]
SORTIE = "data/processed/v0.2/COUVERTURE-RIEBSTEIN.md"

RE_MOT = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ'’-]+")


def tokens(texte):
    return [m.lower() for m in RE_MOT.findall(texte)]


def charger_riebstein():
    entrees = []  # (mot_fr, [mots_ee], section)
    sections = Counter()
    with io.open(RIEBSTEIN, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split(";")
            if len(p) < 5:
                continue
            section, entree, nature, sous, trad = p[0], p[1], p[2], p[3], p[4]
            mots_fr = tokens(entree)
            mots_ee = tokens(trad)
            if not mots_fr or not mots_ee:
                continue
            entrees.append((mots_fr[0], mots_ee, section))
            sections[section] += 1
    return entrees, sections


def charger_corpus():
    voc_fr, voc_ee = set(), set()
    for path in SPLITS:
        with io.open(path, encoding="utf-8") as f:
            next(f)
            for ln in f:
                p = ln.rstrip("\n").split("\t")
                if len(p) < 5:
                    continue
                voc_fr.update(tokens(p[3]))
                voc_ee.update(tokens(p[4]))
    return voc_fr, voc_ee


def main():
    entrees, sections = charger_riebstein()
    voc_fr, voc_ee = charger_corpus()

    n = len(entrees)
    fr_present = sum(1 for mf, _, _ in entrees if mf in voc_fr)
    ee_present = sum(1 for _, me, _ in entrees if any(m in voc_ee for m in me))
    les_deux = sum(1 for mf, me, _ in entrees if mf in voc_fr and any(m in voc_ee for m in me))
    aucun = sum(1 for mf, me, _ in entrees if mf not in voc_fr and not any(m in voc_ee for m in me))

    mots_fr_absents = [mf for mf, _, _ in entrees if mf not in voc_fr]
    mots_ee_absents = []
    for _, me, _ in entrees:
        for m in me:
            if m not in voc_ee:
                mots_ee_absents.append(m)
    top_fr_abs = Counter(mots_fr_absents).most_common(25)
    top_ee_abs = Counter(mots_ee_absents).most_common(25)

    # par section
    par_section = {}
    for mf, me, sec in entrees:
        s = par_section.setdefault(sec, {"total": 0, "fr": 0, "ee": 0})
        s["total"] += 1
        if mf in voc_fr:
            s["fr"] += 1
        if any(m in voc_ee for m in me):
            s["ee"] += 1

    lignes = []
    a = lignes.append
    a("# Couverture du vocabulaire Riebstein dans le corpus v0.2")
    a("")
    a("Rapport généré le 2026-08-14 par `scripts/verif_riebstein.py` (lexique v2 nettoyé).")
    a("")
    a("## Question")
    a("")
    a("Le vocabulaire du lexique Riebstein (8 575 entrées FR→ÉWÉ, 1926) est-il")
    a("**incorporé** dans le corpus parallèle v0.2 (16 050 paires) ?")
    a("")
    a("## Méthode")
    a("")
    a("- **Côté FR** : le mot principal de chaque entrée Riebstein doit apparaître")
    a("  au moins une fois dans les textes français du corpus.")
    a("- **Côté ÉWÉ** : au moins un mot de la traduction éwé Riebstein doit")
    a("  apparaître dans les textes éwé du corpus.")
    a("- Mesure = **couverture lexicale** (présence), pas alignement sémantique.")
    a("")
    a("## Résultats globaux")
    a("")
    a("| Indicateur | Valeur |")
    a("|---|---|")
    a(f"| Entrées Riebstein analysées | {n} |")
    a(f"| Mot FR présent dans le corpus | {fr_present} ({100*fr_present/n:.0f} %) |")
    a(f"| ≥1 mot ÉWÉ présent dans le corpus | {ee_present} ({100*ee_present/n:.0f} %) |")
    a(f"| Mot FR **et** ÉWÉ présents | {les_deux} ({100*les_deux/n:.0f} %) |")
    a(f"| Ni FR ni ÉWÉ présents | {aucun} ({100*aucun/n:.0f} %) |")
    a("")
    a("## Interprétation")
    a("")
    a("> ⚠️ La couverture **FR** mesure si le *mot* du lexique apparaît dans le")
    a("> corpus biblique — mais un verset biblique ne « contient » pas le mot au")
    a("> même sens que l'entrée de dictionnaire. La couverture indique donc la")
    a("> **proximité lexicale**, pas la traduction du terme.")
    a("")
    a("## Couverture par section alphabétique")
    a("")
    a("| Section | Entrées | FR présent | ÉWÉ présent |")
    a("|---|---|---|---|")
    for sec in sorted(par_section):
        s = par_section[sec]
        a(f"| {sec} | {s['total']} | {s['fr']} ({100*s['fr']/s['total']:.0f} %) | {s['ee']} ({100*s['ee']/s['total']:.0f} %) |")
    a("")
    a("## Mots FR du Riebstein absents du corpus (top 25)")
    a("")
    a("| Mot | Fréquence dans Riebstein |")
    a("|---|---|")
    for mot, freq in top_fr_abs:
        a(f"| {mot} | {freq} |")
    a("")
    a("## Mots ÉWÉ du Riebstein absents du corpus (top 25)")
    a("")
    a("| Mot | Fréquence dans Riebstein |")
    a("|---|---|")
    for mot, freq in top_ee_abs:
        a(f"| {mot} | {freq} |")
    a("")
    a("## Conclusion")
    a("")
    pct_fr = 100 * fr_present / n
    pct_ee = 100 * ee_present / n
    a(f"- **Vocabulaire FR** : {pct_fr:.0f} % des mots Riebstein sont présents")
    a(f"  dans le corpus ({n - fr_present} absents, ex. « {top_fr_abs[0][0] if top_fr_abs else '-'} »).")
    a(f"- **Vocabulaire ÉWÉ** : {pct_ee:.0f} % des traductions Riebstein ont au")
    a(f"  moins un mot présent ({len(mots_ee_absents)} mots absents au total).")
    a("- Le corpus est **biblique** : les mots absents sont souvent du vocabulaire")
    a("  courant non-biblique (administration, santé, vie quotidienne) — c'est")
    a("  exactement la lacune que la diversification (piste 1) doit combler.")
    a("")
    a("## Voir aussi")
    a("- Pipeline de nettoyage : `src/clean/`")
    a("- Datasheet : `data/processed/v0.2/DATASHEET.md`")

    with io.open(SORTIE, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")

    print(f"[OK] Rapport écrit : {SORTIE}")
    print(f"Entrées analysées : {n}")
    print(f"FR présent : {fr_present} ({pct_fr:.0f} %)")
    print(f"ÉWÉ présent : {ee_present} ({pct_ee:.0f} %)")
    print(f"Les deux : {les_deux} ({100*les_deux/n:.0f} %)")
    print(f"Aucun : {aucun} ({100*aucun/n:.0f} %)")


if __name__ == "__main__":
    main()
