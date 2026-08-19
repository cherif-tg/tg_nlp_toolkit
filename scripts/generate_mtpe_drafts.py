"""Genere les brouillons MTPE : traduit les phrases FR des grilles en ewe
avec le modele v2 (bidirectionnel), pour post-edition humaine.

Usage :
    python scripts/generate_mtpe_drafts.py           # toutes les grilles
    python scripts/generate_mtpe_drafts.py --max 5   # test (5 phrases)

Sortie : data/mtpe/brouillons-mtpe.csv (separateur ;, UTF-8)
Colonnes : id;grille;sous_thematique;fr;ewe_brouillon;ewe_corrige;note;statut
"""

import argparse
import csv
import glob
import os
import sys
import time

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

BASE = "facebook/nllb-200-distilled-600M"
ADAPTER = "cheriftenga/nllb-200-distilled-600M-ewe-lora-v2"

CODES = {"fr": "fra_Latn", "ewe": "ewe_Latn"}

GRILLES = "data/grilles"
SORTIE = "data/mtpe/brouillons-mtpe.csv"


def id_langue(tokenizer, code):
    """Renvoie l'id du token de langue, avec fallback si le tokenizer
    renvoie l'unk (piege documente sur certaines versions de transformers).
    """
    tid = tokenizer.convert_tokens_to_ids(code)
    if tid == tokenizer.unk_token_id:
        if hasattr(tokenizer, "lang_code_to_id"):
            return tokenizer.lang_code_to_id[code]
        raise ValueError(f"Token de langue introuvable : {code}")
    return tid


def charger():
    print("Chargement du tokenizer et du modele (peut prendre quelques minutes)...")
    tokenizer = AutoTokenizer.from_pretrained(ADAPTER)
    base = AutoModelForSeq2SeqLM.from_pretrained(BASE)
    modele = PeftModel.from_pretrained(base, ADAPTER)
    modele.eval()
    return tokenizer, modele


def traduire_batch(tokenizer, modele, textes, tgt="ewe", max_len=128, beams=4, batch=8):
    tokenizer.src_lang = CODES["fr"]
    tgt_id = id_langue(tokenizer, CODES[tgt])
    resultats = []
    for i in range(0, len(textes), batch):
        lot = textes[i:i + batch]
        enc = tokenizer(
            lot, return_tensors="pt", truncation=True,
            max_length=max_len, padding=True,
        )
        with torch.no_grad():
            gen = modele.generate(
                **enc,
                forced_bos_token_id=tgt_id,
                max_new_tokens=max_len,
                num_beams=beams,
            )
        resultats.extend(tokenizer.batch_decode(gen, skip_special_tokens=True))
    return resultats


def lire_grilles(chemin=GRILLES):
    lignes = []
    for g in sorted(glob.glob(os.path.join(chemin, "*.csv"))):
        nom = os.path.basename(g)
        with open(g, encoding="utf-8") as f:
            lecteur = csv.DictReader(f, delimiter=";")
            for row in lecteur:
                fr = (row.get("Phrase FR") or "").strip()
                if not fr:
                    continue
                lignes.append({
                    "id": (row.get("ID") or "").strip(),
                    "grille": nom,
                    "sous_thematique": (row.get("Sous-thematique") or "").strip(),
                    "fr": fr,
                })
    return lignes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=0, help="Nombre max de phrases (0 = tout)")
    args = parser.parse_args()

    lignes = lire_grilles()
    if args.max > 0:
        lignes = lignes[:args.max]

    print(f"Phrases a traduire : {len(lignes)}")
    if not lignes:
        print("Aucune phrase trouvee dans les grilles.")
        sys.exit(1)

    tokenizer, modele = charger()

    textes = [l["fr"] for l in lignes]
    print("Traduction FR -> EWE (modele v2)...")
    t0 = time.time()
    ewe = traduire_batch(tokenizer, modele, textes)
    duree = time.time() - t0
    print(f"Termine en {duree:.1f} s ({duree / len(textes):.2f} s/phrase)")

    # Verifier le taux de sorties vides
    vides = sum(1 for e in ewe if not e.strip())
    print(f"Sorties vides : {vides}/{len(ewe)}")

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "grille", "sous_thematique", "fr",
                    "ewe_brouillon", "ewe_corrige", "note", "statut"])
        for l, e in zip(lignes, ewe):
            w.writerow([l["id"], l["grille"], l["sous_thematique"], l["fr"],
                        e.strip(), "", "", "A corriger"])
    print(f"Brouillons ecrits : {SORTIE}")


if __name__ == "__main__":
    main()
