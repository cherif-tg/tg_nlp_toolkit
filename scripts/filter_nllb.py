#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
filter_nllb.py — Pipeline de filtrage du corpus NLLB fr-ee (OPUS).

Source : NLLB.ee-fr v1 (ODC-By, publiable avec attribution)
Volume brut : 1 039 385 paires — corpus MINÉ (bruit : fausses paires,
autres langues en éwé : hindi, yoruba…)

Filtres appliqués (dans l'ordre) :
  1. Longueur : >= 4 mots et >= 25 caractères (les deux côtés)
  2. Ratio |ee|/|fr| dans [0.4, 2.5]
  3. Score LASER >= seuil (défaut 1.15)
  4. « éwé-ness » : >= 1 caractère spécial éwé OU >= 1 digraphe typique éwé
     (écarte hindi romanisé, yoruba, etc.)
  5. Pas de lignes suspectes : URLs, trop de chiffres
  6. Dédoublonnage exact (ee, fr)

Sorties :
  - Sous-ensemble filtré  : .openclaw/tmp/nllb_filtered.tsv (non commité, volumineux)
  - Échantillon 100 paires : data/processed/nllb-echantillon-100.csv (commité)
  - Stats de filtrage      : console

Usage : python scripts/filter_nllb.py [--score 1.15] [--seed 42]
"""

import argparse
import csv
import io
import random
import re
import sys
import time

BASE = ".openclaw/tmp/opus-nllb/"
F_EE = BASE + "NLLB.ee-fr.ee"
F_FR = BASE + "NLLB.ee-fr.fr"
F_SC = BASE + "NLLB.ee-fr.scores"
SORTIE_FILTRE = ".openclaw/tmp/nllb_filtered.tsv"
SORTIE_ECH = "data/processed/nllb-echantillon-100.csv"

# Caractères spéciaux de l'éwé moderne (orthographe standardisée)
CAR_EWE = set("ɖɛɔŋɣɸʋƒãẽĩõũɘɨ")
DIGRAPHES_EWE = ("dz", "gb", "kp", "ny", "ts")
# Caractères parasites (hors alphabet latin étendu + éwé) : rejeter
RE_PARASITE = re.compile(r"[^A-Za-zÀ-ÖØ-öø-ÿɖɛɔŋɣɸʋƒãẽĩõũ'’.,;:!?\"() \-]")
# Mots anglais/étrangers fréquents dans les fausses paires (côté éwé) — liste élargie v3
MOTS_ETRANGERS = {
    "the", "and", "not", "for", "with", "that", "this", "you", "have",
    "are", "was", "were", "will", "from", "they", "their", "your", "our",
    "all", "one", "two", "new", "old", "man", "men", "woman", "women",
    "love", "life", "death", "house", "god", "lord", "jesus", "christ",
    "father", "mother", "son", "daughter", "king", "queen", "name", "world",
    "heart", "hand", "eyes", "earth", "heaven", "noone", "destooled",
    "rengbe", "undoro", "hliadzi", "hamesha", "tere",
    "who", "what", "when", "where", "how", "why", "but", "can", "cannot",
    "may", "shall", "should", "would", "could", "said", "say", "make",
    "made", "know", "think", "give", "take", "go", "went", "come", "back",
    "into", "upon", "under", "over", "again", "more", "most", "some", "any",
    "many", "much", "such", "only", "very", "just", "also", "even", "still",
    "well", "now", "then", "there", "here", "his", "her", "them", "day",
    "days", "night", "water", "fire", "people", "land", "word", "thing",
    "things", "great", "good", "bad", "fear", "won", "vs", "discover",
    "defeats", "anyone", "diets", "eye", "fichajes", "de", "la", "el", "los",
    "las", "un", "una", "kanye", "coinye", "ajagba", "kiladze", "tsintsadze",
}
RE_URL = re.compile(r"https?://|www\.")
RE_CHIFFRES = re.compile(r"\d")


def est_ewe(texte: str) -> bool:
    """Indice renforcé : >= 2 marqueurs éwé DISTINCTS et pas de mot étranger."""
    if RE_PARASITE.search(texte):
        return False
    bas = texte.lower()
    marqueurs = set()
    for ch in bas:
        if ch in CAR_EWE:
            marqueurs.add(ch)
    for d in DIGRAPHES_EWE:
        if d in bas:
            marqueurs.add(d)
    if len(marqueurs) < 2:
        return False
    mots = set(re.findall(r"[a-zà-öø-ÿɖɛɔŋɣɸʋƒ]+", bas))
    return not (mots & MOTS_ETRANGERS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--score", type=float, default=1.15, help="Seuil score LASER")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    t0 = time.time()
    total = gardees = 0
    rejet_longueur = rejet_ratio = rejet_score = rejet_langue = rejet_url = 0
    doubles = 0
    vus = set()
    gardees_liste = []

    with io.open(F_EE, encoding="utf-8") as a, \
         io.open(F_FR, encoding="utf-8") as b, \
         io.open(F_SC, encoding="utf-8") as c, \
         io.open(SORTIE_FILTRE, "w", encoding="utf-8") as out:
        out.write("fr\tewe\tscore\n")
        for ee, fr, sc in zip(a, b, c):
            ee = ee.rstrip("\n")
            fr = fr.rstrip("\n")
            total += 1
            try:
                score = float(sc.strip())
            except ValueError:
                score = 0.0

            nf, ne = len(fr.split()), len(ee.split())
            if nf < 4 or ne < 4 or len(fr) < 25 or len(ee) < 25:
                rejet_longueur += 1
                continue
            ratio = ne / nf
            if not (0.4 <= ratio <= 2.5):
                rejet_ratio += 1
                continue
            if score < args.score:
                rejet_score += 1
                continue
            if not est_ewe(ee):
                rejet_langue += 1
                continue
            if RE_URL.search(fr) or RE_URL.search(ee) or len(RE_CHIFFRES.findall(fr)) > 4:
                rejet_url += 1
                continue
            cle = (ee.lower(), fr.lower())
            if cle in vus:
                doubles += 1
                continue
            vus.add(cle)
            gardees += 1
            gardees_liste.append((fr, ee, score))
            out.write(f"{fr}\t{ee}\t{score:.4f}\n")
            if total % 250000 == 0:
                print(f"  ... {total:,} lues, {gardees:,} gardées ({time.time()-t0:.0f}s)")

    print(f"\n=== FILTRAGE NLLB fr-ee ===")
    print(f"Lues            : {total:,}")
    print(f"Rejet longueur  : {rejet_longueur:,}")
    print(f"Rejet ratio     : {rejet_ratio:,}")
    print(f"Rejet score     : {rejet_score:,}")
    print(f"Rejet langue    : {rejet_langue:,}")
    print(f"Rejet URL/chiffres : {rejet_url:,}")
    print(f"Doublons        : {doubles:,}")
    print(f"GARDÉES         : {gardees:,}  ({100*gardees/total:.1f} %)")

    # Échantillon de vérification : 50 avec caractères spéciaux + 50 sans
    random.seed(args.seed)
    avec = [p for p in gardees_liste if any(ch in CAR_EWE for ch in p[1])]
    sans = [p for p in gardees_liste if not any(ch in CAR_EWE for ch in p[1])]
    ech = random.sample(avec, min(50, len(avec))) + random.sample(sans, min(50, len(sans)))
    random.shuffle(ech)

    with io.open(SORTIE_ECH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "fr", "ewe", "score", "statut"])
        for i, (fr, ee, sc) in enumerate(ech, 1):
            w.writerow([i, fr, ee, f"{sc:.4f}", ""])

    print(f"\nÉchantillon : {len(ech)} paires -> {SORTIE_ECH}")
    print(f"  (dont {len(avec)}+ paires avec caractères spéciaux éwé, {len(sans)}+ sans)")
    print(f"Sous-ensemble filtré : {SORTIE_FILTRE}")
    print(f"Durée : {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
