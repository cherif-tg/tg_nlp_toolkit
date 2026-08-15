#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI de traduction batch FR <-> EWE (phase P3).

Traduit un fichier CSV entier (campagnes de messages, questionnaires,
listes de phrases) d'une langue a l'autre.

Usage :

    # Mode local (le CLI charge le modele lui-meme)
    python -m src.cli.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv

    # Mode API (le CLI appelle l'API REST deja lancee - modele deja charge)
    python -m src.cli.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv --api http://127.0.0.1:8000

Le fichier d'entree est un CSV avec une colonne de texte. La colonne est
detectee automatiquement ("text", "texte", "fr", "phrase", "message",
"ewe") ou donnee avec --colonne. Le fichier de sortie reprend toutes les
colonnes d'origine + une colonne "traduction".

Le CLI reutilise la meme logique que l'API : src/api/inference.py
(mode local) ou l'endpoint /translate de l'API (mode API).
"""

import argparse
import sys
import time

import pandas as pd

# Colonnes candidates pour detecter automatiquement le texte source
COLONNES_AUTO = ["text", "texte", "fr", "phrase", "message", "ewe"]


def choisir_colonne(df, colonne):
    """Determine la colonne contenant le texte a traduire."""
    if colonne:
        if colonne not in df.columns:
            raise SystemExit(
                f"Colonne introuvable : '{colonne}'. "
                f"Colonnes presentes : {list(df.columns)}"
            )
        return colonne
    for candidat in COLONNES_AUTO:
        if candidat in df.columns:
            return candidat
    return df.columns[0]


def lire_csv(chemin):
    """Lit un CSV (virgule ou tabulation) sans se tromper sur les
    phrases contenant des espaces ou des virgules."""
    with open(chemin, encoding="utf-8", errors="replace") as f:
        extrait = f.read(2048)
    separateur = "\t" if ("\t" in extrait and "," not in extrait) else ","
    return pd.read_csv(chemin, sep=separateur, on_bad_lines="skip")


def traduire_lot(texte, src, tgt, beams, api_url):
    """Traduit une phrase : via l'API (--api) ou en local."""
    if api_url:
        import httpx

        reponse = httpx.post(
            f"{api_url}/translate",
            json={"text": texte, "src": src, "tgt": tgt},
            timeout=120,
        )
        reponse.raise_for_status()
        return reponse.json()["traduction"]
    from src.api.inference import traduire

    return traduire(texte, src=src, tgt=tgt, beams=beams)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Traduction batch FR <-> EWE (campagnes, questionnaires)."
    )
    parser.add_argument("--input", required=True,
                        help="Fichier CSV d'entree (phrases a traduire)")
    parser.add_argument("--output", required=True,
                        help="Fichier CSV de sortie (avec colonne traduction)")
    parser.add_argument("--src", default="fr", choices=["fr", "ewe"],
                        help="Langue source (defaut : fr)")
    parser.add_argument("--tgt", default="ewe", choices=["ewe", "fr"],
                        help="Langue cible (defaut : ewe)")
    parser.add_argument("--colonne", default=None,
                        help="Nom de la colonne de texte (auto si absent)")
    parser.add_argument("--beams", type=int, default=4,
                        help="Taille du faisceau, beam search (defaut : 4)")
    parser.add_argument("--api", default=None,
                        help="URL de l'API REST (ex. http://127.0.0.1:8000) ; "
                             "sinon le modele est charge localement")
    args = parser.parse_args(argv)

    if args.src == args.tgt:
        raise SystemExit("src et tgt doivent etre differents")

    print(f"Lecture de {args.input} ...")
    try:
        df = lire_csv(args.input)
    except FileNotFoundError:
        raise SystemExit(f"Fichier introuvable : {args.input}")
    except Exception as e:
        raise SystemExit(f"Lecture impossible de {args.input} : {e}")

    if df.empty:
        raise SystemExit("Le fichier d'entree est vide.")

    colonne = choisir_colonne(df, args.colonne)
    print(f"Colonne source : '{colonne}' ({len(df)} ligne(s))")
    print(f"Direction : {args.src} -> {args.tgt}")
    if args.api:
        print(f"Mode API : {args.api}")
    else:
        print("Mode local : chargement du modele (patienter au premier "
              "lancement)...")

    # Traduction ligne a ligne, avec affichage de progression
    debut = time.time()
    resultats = []
    total = len(df)
    for i, valeur in enumerate(df[colonne].tolist(), start=1):
        texte = str(valeur) if pd.notna(valeur) else ""
        if not texte.strip():
            resultats.append("")  # cellule vide -> traduction vide
            continue
        resultats.append(traduire_lot(texte, args.src, args.tgt,
                                      args.beams, args.api))
        if i % 25 == 0 or i == total:
            print(f"  {i}/{total} traduites")

    df["traduction"] = resultats
    df.to_csv(args.output, index=False, encoding="utf-8")
    duree = time.time() - debut
    print(f"Termine : {total} ligne(s) en {duree:.1f} s -> {args.output}")


if __name__ == "__main__":
    main()
