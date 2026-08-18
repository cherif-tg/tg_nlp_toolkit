#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_public.py - Met a jour le dataset HF v0.3 et le passe en PUBLIC.

Etapes :
1. Verification du contenu du dossier huggingface/
2. Upload des fichiers (dataset card, datasheet, splits, reference)
3. Passage du dataset en public (update_repo_visibility)

Usage :
  python scripts/publish_public.py --dry-run   # verifier sans rien envoyer
  python scripts/publish_public.py             # upload + public

Le token HF vient du cache (login deja effectue) ou est demande.
"""

import argparse
import os
import sys

DOSSIER = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "huggingface")
)
REPO_ID = "cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3"

FICHIERS = [
    "readme.md",
    "DATASHEET.md",
    "train.tsv",
    "dev.tsv",
    "test.tsv",
    "test-reference-final.tsv",
    "riebstein-lexique-v2.tsv",
    "licence-bible-ewe-1913.md",
    "licence-segond-1910.md",
]


def verifier():
    manquants = []
    tailles = {}
    for nom in FICHIERS:
        chemin = os.path.join(DOSSIER, nom)
        if os.path.isfile(chemin):
            tailles[nom] = os.path.getsize(chemin)
        else:
            manquants.append(nom)
    return manquants, tailles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Verifier sans envoyer")
    args = parser.parse_args()

    manquants, tailles = verifier()
    print("=== Contenu du dossier huggingface/ ===")
    for nom, taille in tailles.items():
        print(f"  {nom} ({taille/1024:.1f} Ko)")
    if manquants:
        print("MANQUANTS :", manquants)
        sys.exit(1)

    if args.dry_run:
        print("\nDry-run : rien envoye. Tout est pret.")
        return

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Erreur : huggingface_hub manquant.")
        sys.exit(1)

    api = HfApi()
    try:
        api.whoami()
    except Exception:
        print("Non connecte : colle ton token Write HF.")
        from huggingface_hub import login
        login()

    print(f"\n=== Upload vers {REPO_ID} ===")
    for nom in FICHIERS:
        chemin = os.path.join(DOSSIER, nom)
        print(f"  upload {nom}...")
        api.upload_file(
            path_or_fileobj=chemin,
            path_in_repo=nom,
            repo_id=REPO_ID,
            repo_type="dataset",
        )

    print("\n=== Passage en PUBLIC ===")
    api.update_repo_visibility(repo_id=REPO_ID, repo_type="dataset", private=False)
    print(f"Dataset {REPO_ID} est maintenant PUBLIC.")
    print(f"https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
