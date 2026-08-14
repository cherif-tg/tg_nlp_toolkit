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
import sys

REPO_ID = "cheriftenga/tg-nlp-toolkit-fr-ewe-v0.2"
DOSSIER = "huggingface"


def main():
    parser = argparse.ArgumentParser(description="Publication du corpus sur HuggingFace")
    parser.add_argument("--public", action="store_true",
                        help="Créer le dépôt en PUBLIC (défaut : privé)")
    args = parser.parse_args()

    try:
        from huggingface_hub import HfApi, login
    except ImportError:
        print("❌ huggingface_hub manquant. Installe :  pip install huggingface_hub")
        sys.exit(1)

    print("🔑 Connecte-toi à HuggingFace (colle ton token Write)…")
    login()

    api = HfApi()
    private = not args.public

    print(f"📦 Création du dataset '{REPO_ID}' (privé={private})…")
    api.create_repo(repo_id=REPO_ID, repo_type="dataset", private=private, exist_ok=True)

    print(f"⬆️ Upload du dossier '{DOSSIER}/'…")
    api.upload_folder(repo_id=REPO_ID, repo_type="dataset", folder_path=DOSSIER)

    print()
    print("✅ Publication terminée !")
    if private:
        print("   Le dataset est PRIVÉ. Vérifie-le, puis passe-le en public :")
        print("   https://huggingface.co/settings (onglet du dataset > Settings > Make public)")
    else:
        print("   Le dataset est PUBLIC : https://huggingface.co/datasets/" + REPO_ID)


if __name__ == "__main__":
    main()
