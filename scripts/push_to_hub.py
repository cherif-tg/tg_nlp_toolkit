#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
push_to_hub.py — Publie le corpus v0.2 sur HuggingFace (dataset).

Usage :
  python scripts/push_to_hub.py            # création privée + upload (recommandé)
  python scripts/push_to_hub.py --public   # créer directement en public (après vérification !)

Le token HF est demandé de façon interactive (jamais stocké dans le repo).
Réglages HuggingFace > Access Tokens > "Write" token.
"""

import argparse
import os
import sys

# Chemin absolu du dossier de publication : fonctionne quel que soit le
# répertoire depuis lequel le script est lancé.
DOSSIER = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "huggingface")
)
REPO_ID = "cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3"


def main():
    parser = argparse.ArgumentParser(description="Publication du corpus sur HuggingFace")
    parser.add_argument("--public", action="store_true",
                        help="Créer le dépôt en PUBLIC (défaut : privé)")
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("Erreur : huggingface_hub manquant. Installe :  pip install huggingface_hub")
        sys.exit(1)

    print("Connexion a HuggingFace (colle ton token Write)...")
    login()

    api = HfApi()
    private = not args.public

    print(f"Creation du dataset '{REPO_ID}' (prive={private})...")
    api.create_repo(repo_id=REPO_ID, repo_type="dataset", private=private, exist_ok=True)

    print(f"Upload du dossier '{DOSSIER}'...")
    if not os.path.isdir(DOSSIER):
        print(f"Erreur : dossier introuvable : {DOSSIER}")
        print("   Vérifie que le dossier huggingface/ existe à la racine du projet.")
        sys.exit(1)
    api.upload_folder(repo_id=REPO_ID, repo_type="dataset", folder_path=DOSSIER)

    print()
    print("Publication terminee !")
    if private:
        print("   Le dataset est PRIVÉ. Vérifie-le, puis passe-le en public :")
        print("   https://huggingface.co/settings (onglet du dataset > Settings > Make public)")
    else:
        print("   Le dataset est PUBLIC : https://huggingface.co/datasets/" + REPO_ID)


if __name__ == "__main__":
    main()
