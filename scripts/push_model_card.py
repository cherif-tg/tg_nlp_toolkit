#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pousse la model card du modele LoRA vers HuggingFace.

Usage :
    python scripts/push_model_card.py

Avant de lancer : etre connecte a HuggingFace (token Write).
    from huggingface_hub import notebook_login
    notebook_login()
"""

import os

from huggingface_hub import HfApi

REPO_ID = "cheriftenga/nllb-200-distilled-600M-ewe-lora"
MODEL_CARD = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "huggingface",
    "model-card-ewe-lora",
    "README.md",
)


def main():
    if not os.path.isfile(MODEL_CARD):
        raise SystemExit(f"Model card introuvable : {MODEL_CARD}")

    api = HfApi()
    print(f"Upload de la model card vers {REPO_ID} ...")
    api.upload_file(
        path_or_fileobj=MODEL_CARD,
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="model",
    )
    print("Model card publiee :")
    print(f"  https://huggingface.co/{REPO_ID}")


if __name__ == "__main__":
    main()
