#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_reference_test.py — Test de référence de 300 paires (piste 3).

Objectif : un test set VÉRIFIÉ À 100 % par 2+ locuteurs natifs, servant de
référence officielle d'évaluation (les splits v0.3 restent approximatifs).

Méthode :
- Échantillonnage depuis le split test de la v0.3 (jamais utilisé en
  entraînement) : 150 paires Bible + 150 paires NLLB (seed 42)
- Colonnes de vérification pour 2 locuteurs indépendants (verif1, verif2)
  + commentaire
- Un guide de vérification est généré : docs/GUIDE-VERIFICATION.md

Sortie : data/processed/v0.3/test-reference-300.csv
Usage : python scripts/make_reference_test.py
"""

import csv
import io
import random

TEST = "data/processed/v0.3/test.tsv"
SORTIE = "data/processed/v0.3/test-reference-300.csv"
GUIDE = "docs/GUIDE-VERIFICATION.md"
SEED = 42
N_BIBLE = 150
N_NLLB = 150


def charger_test():
    bible, nllb = [], []
    with io.open(TEST, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            if len(p) < 3:
                continue
            source, fr, ewe = p[0], p[1], p[2]
            (bible if source == "bible" else nllb).append((fr, ewe))
    return bible, nllb


def main():
    bible, nllb = charger_test()
    rng = random.Random(SEED)
    rng.shuffle(bible)
    rng.shuffle(nllb)
    sel = [( "bible", fr, ewe) for fr, ewe in bible[:N_BIBLE]]
    sel += [("nllb", fr, ewe) for fr, ewe in nllb[:N_NLLB]]
    rng.shuffle(sel)

    with io.open(SORTIE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "source", "fr", "ewe", "verif1", "verif2", "commentaire"])
        for i, (source, fr, ewe) in enumerate(sel, 1):
            w.writerow([i, source, fr, ewe, "", "", ""])

    # Guide de vérification
    with io.open(GUIDE, "w", encoding="utf-8") as f:
        f.write(f"""# Guide de vérification — Test de référence (300 paires)

## Objectif

Ce jeu de **{N_BIBLE + N_NLLB} paires** (150 Bible + 150 NLLB) est la
**référence officielle d'évaluation** du projet : il doit être vérifié à
**100 %** par **au moins 2 locuteurs natifs indépendants** (double
validation). Les paires rejetées seront exclues ; seules les paires validées
par les deux vérificateurs resteront dans la référence finale.

## Consignes

Pour chaque ligne du fichier `test-reference-300.csv` :

1. Lis la phrase **française** (colonne `fr`).
2. Lis la traduction **éwé** (colonne `ewe`).
3. Évalue la qualité de la correspondance :
   - **ok** : traduction correcte, sens fidèle (les petites différences de
     formulation sont acceptables si le sens est bon)
   - **corriger** : la traduction est éwé correct mais la correspondance est
     approximative / il y a des résidus / une partie manque
   - **à-rejeter** : la traduction est fausse, incomplète, dans une autre
     langue, ou ne correspond pas du tout

4. Écris ta décision dans TA colonne (`verif1` pour le 1er locuteur,
   `verif2` pour le 2e). N'écris jamais dans la colonne de l'autre.
5. Optionnel : mets une note dans `commentaire` (ex. « manque la fin »,
   « orthographe ancienne mais correct »).

## Exemples de cas

| Cas | Décision |
|---|---|
| « Le médicament doit être pris matin et soir » → `Atike la wòle be woano ŋdi kple fiẽ` | ok |
| « Je vais à l'école » → traduction correcte mais parle d'autre chose | à-rejeter |
| Éwé correct mais phrase française tronquée | corriger |
| Texte en anglais ou autre langue | à-rejeter |

## Rappel (politique de variantes)

- La composante **Bible** est en éwé historique (1913) : l'orthographe peut
  différer de l'éwé moderne — jugez le SENS, pas l'orthographe.
- La composante **NLLB** est en éwé moderne (parfois approximatif).

## Après la vérification

Renvoyez le fichier rempli au coordinateur (Cherif). Les deux colonnes seront
croisées : désaccords → arbitrage ; consensus ok → référence finale.
""")

    print(f"[OK] {len(sel)} paires -> {SORTIE}")
    print(f"     Guide -> {GUIDE}")
    print(f"     Bible: {sum(1 for s,_,_ in sel if s=='bible')} | NLLB: {sum(1 for s,_,_ in sel if s=='nllb')}")


if __name__ == "__main__":
    main()
