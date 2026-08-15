#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_notebooks.py — Genere les notebooks Colab de la Phase D :
  1. notebooks/01-baseline-nllb.ipynb   (zero-shot + evaluation)
  2. notebooks/02-finetune-lora.ipynb   (fine-tuning LoRA + comparaison)

Conventions (regles du projet) :
  - Aucun emoji dans le code ni dans les cellules (markdown inclus).
  - Chaque bloc de code est explique en francais avant execution.
  - Les donnees sont chargees depuis le repo GitHub public
    (cherif-tg/tg_nlp_toolkit) — zero upload manuel sur Colab.
  - Cellule de diagnostic GPU en tete de chaque notebook.
"""

import json
import os


def md(texte):
    return {"cell_type": "markdown", "metadata": {}, "source": texte.splitlines(keepends=True)}


def code(texte):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": texte.splitlines(keepends=True),
    }


def notebook(cells, titre):
    return {
        "cells": cells,
        "metadata": {
            "colab": {"provenance": []},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "title": titre,
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


# Cellule de diagnostic GPU (commune aux deux notebooks)
CELLULE_GPU = code("""# Diagnostic GPU
# Colab fournit un GPU (T4) gratuitement, mais il faut l'activer :
#   menu Executer > Changer le type d'execution > T4 GPU
#   puis Executer > Redemarrer la session (obligatoire).
import torch

print("CUDA disponible :", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU :", torch.cuda.get_device_name(0))
    print("Memoire :", round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1), "Go")
else:
    print("Attention : execution sur CPU (lent). Active le GPU T4 puis redemarre la session.")
    print("Si Colab ne propose pas de GPU (quota), utilise Kaggle : Accelerator > GPU T4.")""")


# =========================================================================
# NOTEBOOK 1 — BASELINE NLLB (zero-shot)
# =========================================================================
n1 = [
    md("""# 1. Baseline : NLLB-200 (zero-shot) FR <-> Ewe

**Objectif** : mesurer la qualite de traduction du modele **NLLB-200-distilled-600M**
(Meta AI) sur notre corpus de test **sans aucun entrainement** (mode "zero-shot").

C'est la **reference de depart** : tout le travail de fine-tuning (notebook 2)
devra faire mieux que ces scores.

## Comment ca marche ?

- **NLLB** ("No Language Left Behind") est un modele de traduction multilingue
  entraine sur 200 langues, dont l'**ewe** (code `ewe_Latn`).
- Il est **"zero-shot"** pour nous : il n'a jamais vu notre corpus, mais il a vu
  de l'ewe pendant son entrainement.
- On mesure la qualite avec deux metriques standard :
  - **chrF++** (la metrique principale du projet, robuste aux petites variations)
  - **BLEU** (metrique classique, plus stricte)

> Le test set est charge depuis le **repo GitHub public** du projet.
> C'est le split `test.tsv` : 6 564 paires jamais utilisees pour l'entrainement."""),

    code("""# Installation des bibliotheques necessaires
# - transformers : modeles HuggingFace (NLLB)
# - sacrebleu    : metriques chrF++ et BLEU
# - pandas       : lecture des fichiers TSV
# - sentencepiece : tokenizer de NLLB (obligatoire)
!pip install -q transformers sacrebleu pandas sentencepiece datasets

print("Dependances installees")"""),

    CELLULE_GPU,

    code("""# Imports
import torch
import pandas as pd
import sacrebleu
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device utilise :", device)"""),

    code("""# Chargement du jeu de test depuis le repo GitHub public
URL_TEST = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/data/processed/v0.3/test.tsv"

try:
    df = pd.read_csv(URL_TEST, sep="\\t")
    print("Test set charge :", len(df), "paires FR<->Ewe")
    print(df.head(3))
except Exception as e:
    print("Telechargement GitHub impossible :", e)
    print("Solution : telecharge test.tsv depuis le repo et execute :")
    print("  from google.colab import files; upload = files.upload()")"""),

    code("""# Chargement du modele NLLB-200-distilled-600M
# 600M parametres = version "distilled" (legere), adaptee a un GPU gratuit.
MODEL_NAME = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# Verification des codes de langue
assert "fra_Latn" in tokenizer.additional_special_tokens, "francais absent"
assert "ewe_Latn" in tokenizer.additional_special_tokens, "ewe absent"
print("Modele charge - codes langue : fra_Latn (fr), ewe_Latn (ewe)")"""),

    code("""# Fonction de traduction en batch
# - src / tgt : codes de langue NLLB (fra_Latn, ewe_Latn)
# - num_beams=4 : recherche en faisceau (meilleure qualite que greedy)
# - Le tokenizer doit connaitre la langue SOURCE avant d'encoder.

def traduire(textes, src="fra_Latn", tgt="ewe_Latn", max_len=128, batch_size=16):
    tokenizer.src_lang = src
    resultats = []
    for i in range(0, len(textes), batch_size):
        lot = textes[i:i + batch_size]
        enc = tokenizer(lot, return_tensors="pt", padding=True,
                        truncation=True, max_length=max_len).to(device)
        with torch.no_grad():
            gen = model.generate(
                **enc,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt),
                max_new_tokens=max_len,
                num_beams=4,
            )
        resultats += tokenizer.batch_decode(gen, skip_special_tokens=True)
    return resultats

print("Fonction de traduction prete")"""),

    code("""# Evaluation FR -> EWE (le sens qui nous interesse le plus)
# On traduit les 6 564 phrases francaises du test set, puis on compare
# aux traductions ewe de reference avec chrF++ et BLEU.

preds_fr_ee = traduire(df["fr"].tolist(), src="fra_Latn", tgt="ewe_Latn")
refs_ee = df["ewe"].tolist()

chrf_fr_ee = sacrebleu.corpus.chrf(preds_fr_ee, [refs_ee])
bleu_fr_ee = sacrebleu.corpus.bleu(preds_fr_ee, [refs_ee])

print("FR -> EWE (zero-shot)")
print("   chrF++ :", round(chrf_fr_ee.score, 2))
print("   BLEU   :", round(bleu_fr_ee.score, 2))

# Afficher 3 exemples concrets
for i in range(3):
    print("--- Exemple", i + 1, "---")
    print("FR :", df['fr'].iloc[i])
    print("Ref:", refs_ee[i])
    print("Pred:", preds_fr_ee[i])"""),

    code("""# Evaluation EWE -> FR (sens inverse)
preds_ee_fr = traduire(df["ewe"].tolist(), src="ewe_Latn", tgt="fra_Latn")
refs_fr = df["fr"].tolist()

chrf_ee_fr = sacrebleu.corpus.chrf(preds_ee_fr, [refs_fr])
bleu_ee_fr = sacrebleu.corpus.bleu(preds_ee_fr, [refs_fr])

print("EWE -> FR (zero-shot)")
print("   chrF++ :", round(chrf_ee_fr.score, 2))
print("   BLEU   :", round(bleu_ee_fr.score, 2))

print("Tableau de bord baseline :")
print("   FR->EWE : chrF++", round(chrf_fr_ee.score, 2), "| BLEU", round(bleu_fr_ee.score, 2))
print("   EWE->FR : chrF++", round(chrf_ee_fr.score, 2), "| BLEU", round(bleu_ee_fr.score, 2))"""),

    md("""## Comment interpreter ces scores ?

- **chrF++ 40-55** sur cette tache : le modele "se debrouille" (le vocabulaire
  religieux est bien connu de NLLB).
- **BLEU bas (< 15)** : normal, BLEU est tres strict sur les mots exacts, et
  l'ewe de 1913 a une orthographe differente de l'ewe moderne vu par NLLB.
- Ces scores sont notre **reference** : le notebook 2 (fine-tuning LoRA sur
  notre corpus) doit les **depasser**, surtout en chrF++.

> Si le score est tres bas, verifie que le GPU est actif
> (menu Executer > Changer le type d'execution > T4 GPU)."""),
]

# =========================================================================
# NOTEBOOK 2 — FINE-TUNING LoRA
# =========================================================================
n2 = [
    md("""# 2. Fine-tuning de NLLB avec LoRA sur notre corpus

**Objectif** : adapter NLLB-200-distilled-600M a NOTRE corpus (ewe 1913 +
segond 1910 + NLLB filtre) avec **LoRA** (Low-Rank Adaptation), pour depasser
la baseline.

## Pourquoi LoRA et pas un fine-tuning complet ?

- Un fine-tuning complet modifierait les **600M de parametres** : GPU sature,
  heures d'entrainement, risque d'oubli catastrophique.
- **LoRA** ne modifie que de petits "adaptateurs" (~0,5 % des parametres)
  ajoutes aux couches d'attention : rapide, leger, et le modele de base reste
  intact.
- Resultat : ~20-40 min d'entrainement sur un T4 gratuit pour 3 epoques.

## Pipeline

1. Charger `train.tsv` (52 512 paires) et `dev.tsv` (6 564 paires) depuis GitHub
2. Tokeniser les paires (langue source + langue cible NLLB)
3. Ajouter les adaptateurs LoRA
4. Entrainer avec `Seq2SeqTrainer` (HuggingFace)
5. Evaluer sur `test.tsv` et **comparer avec la baseline** (notebook 1)"""),

    code("""# Installation (peft = bibliotheque officielle LoRA de HuggingFace)
!pip install -q transformers sacrebleu pandas sentencepiece datasets peft accelerate

print("Dependances installees")"""),

    CELLULE_GPU,

    code("""# Imports
import torch
import pandas as pd
import sacrebleu
import numpy as np
from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM,
                          Seq2SeqTrainer, Seq2SeqTrainingArguments,
                          DataCollatorForSeq2Seq)
from datasets import Dataset
from peft import LoraConfig, get_peft_model

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device utilise :", device)"""),

    code("""# Chargement train / dev / test depuis le repo GitHub public
BASE = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/data/processed/v0.3/"

def charger(nom):
    return pd.read_csv(BASE + nom, sep="\\t")

train = charger("train.tsv")
dev   = charger("dev.tsv")
test  = charger("test.tsv")
print("train =", len(train), "| dev =", len(dev), "| test =", len(test))
print(train.head(2))"""),

    code("""# Chargement du modele + tokenizer
MODEL_NAME = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# On gelee le modele de base : seuls les adaptateurs LoRA seront entrainables.
model.config.use_cache = False  # requis par le Trainer pendant l'entrainement
print("Modele charge")"""),

    code("""# Preparation des donnees au format attendu par le Trainer
# Chaque exemple : "input_ids" = phrase source tokenisee (langue source),
#                  "labels"   = phrase cible tokenisee (langue cible).
# Le tokenizer NLLB encode la langue via src_lang et forced_bos_token_id.

def tokeniser(sources, cibles):
    tokenizer.src_lang = "fra_Latn"
    enc = tokenizer(sources, padding=True, truncation=True, max_length=128,
                    return_tensors="pt")
    tokenizer.src_lang = "ewe_Latn"
    labels = tokenizer(cibles, padding=True, truncation=True, max_length=128,
                       return_tensors="pt")
    enc["labels"] = labels["input_ids"].clone()
    # -100 = tokens ignores par la loss (padding)
    enc["labels"][enc["labels"] == tokenizer.pad_token_id] = -100
    return {k: v.numpy() for k, v in enc.items()}

train_ds = Dataset.from_list(
    [tokeniser([fr], [ee]) for fr, ee in zip(train["fr"], train["ewe"])]
)
dev_ds = Dataset.from_list(
    [tokeniser([fr], [ee]) for fr, ee in zip(dev["fr"], dev["ewe"])]
)
print("Datasets prets : train", len(train_ds), "| dev", len(dev_ds))
print("Exemple de cles :", list(train_ds[0].keys()))"""),

    code("""# Configuration LoRA
# On ajoute des adaptateurs sur les projections Q et V de l'attention
# (cible classique pour les modeles seq2seq).
lora_config = LoraConfig(
    r=16,                 # rang de la factorisation (plus = plus de capacite)
    lora_alpha=32,        # echelle de mise a jour (souvent 2 x r)
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,    # regularisation
    bias="none",
    task_type="SEQ_2_SEQ_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Attendu : ~0,5 % des parametres entrainables seulement !"""),

    code("""# Metrique d'evaluation pendant l'entrainement : chrF++ sur le dev set
def compute_metrics(eval_pred):
    preds, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    refs = [[r] for r in decoded_labels]
    chrf = sacrebleu.corpus.chrf(decoded_preds, refs)
    return {"chrF++": chrf.score}

collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
print("Metrique + collator prets")"""),

    code("""# Configuration de l'entrainement (adaptee a un T4 gratuit)
training_args = Seq2SeqTrainingArguments(
    output_dir="nllb-ewe-lora",
    num_train_epochs=3,             # 3 passages sur le corpus
    per_device_train_batch_size=8,  # 8 paires par lot (T4 ~ 16 Go)
    per_device_eval_batch_size=8,
    learning_rate=3e-4,
    warmup_steps=200,
    weight_decay=0.01,
    logging_steps=50,
    eval_strategy="epoch",          # evaluation a chaque fin d'epoque
    save_strategy="epoch",
    predict_with_generate=True,     # genere de vraies traductions pour la metrique
    generation_max_length=128,
    fp16=True,                      # demi-precision : plus rapide sur T4
    report_to="none",
    push_to_hub=False,
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=dev_ds,
    data_collator=collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

print("Trainer pret - lance l'entrainement avec la cellule suivante")"""),

    code("""# LANCEMENT DE L'ENTRAINEMENT (~20-40 min sur T4)
trainer.train()

print("Entrainement termine !")"""),

    code("""# Evaluation finale sur le TEST set (jamais vu par le modele)
def traduire_model(textes, tgt="ewe_Latn", max_len=128, batch_size=16):
    tokenizer.src_lang = "fra_Latn"
    resultats = []
    for i in range(0, len(textes), batch_size):
        lot = textes[i:i + batch_size]
        enc = tokenizer(lot, return_tensors="pt", padding=True,
                        truncation=True, max_length=max_len).to(device)
        with torch.no_grad():
            gen = model.generate(
                **enc,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt),
                max_new_tokens=max_len,
                num_beams=4,
            )
        resultats += tokenizer.batch_decode(gen, skip_special_tokens=True)
    return resultats

preds = traduire_model(test["fr"].tolist())
refs = test["ewe"].tolist()
chrf = sacrebleu.corpus.chrf(preds, [refs])
bleu = sacrebleu.corpus.bleu(preds, [refs])

print("FR -> EWE apres fine-tuning LoRA")
print("   chrF++ :", round(chrf.score, 2), " (a comparer avec la baseline)")
print("   BLEU   :", round(bleu.score, 2))

for i in range(3):
    print("--- Exemple", i + 1, "---")
    print("FR :", test['fr'].iloc[i])
    print("Ref:", refs[i])
    print("Pred:", preds[i])"""),

    code("""# Sauvegarde du modele + export vers HuggingFace (optionnel)
# 1) Sauvegarde locale (dossier modele complet)
model.save_pretrained("nllb-ewe-lora-final")
tokenizer.save_pretrained("nllb-ewe-lora-final")
print("Modele sauvegarde dans nllb-ewe-lora-final/")

# 2) Export vers ton compte HuggingFace (cheriftenga)
# Decommente et execute APRES t'etre connecte :
#   from huggingface_hub import notebook_login
#   notebook_login()   # colle ton token (Settings > Access Tokens)
#
#   model.push_to_hub("cheriftenga/nllb-200-distilled-600M-ewe-lora")
#   tokenizer.push_to_hub("cheriftenga/nllb-200-distilled-600M-ewe-lora")
print("Pret pour l'export (voir instructions commentees)")"""),

    md("""## Lecture des resultats

- Si **chrF++ fine-tune > chrF++ baseline** (notebook 1) : notre corpus apporte
  un vrai gain -> le corpus v0.3 est **utile et publiable**.
- Si le gain est faible : verifier (a) le nombre d'epoques, (b) le `r` de LoRA,
  (c) la taille du corpus. Les donnees restent la contrainte principale en
  low-resource.

**Prochaines etapes** : demo Gradio (P3), publication HuggingFace,
puis traduction manuelle des grilles (10 themes) pour couvrir le domaine
sante/administration."""),
]


def main():
    os.makedirs("notebooks", exist_ok=True)
    cibles = {
        "notebooks/01-baseline-nllb.ipynb": notebook(n1, "Baseline NLLB FR-Ewe"),
        "notebooks/02-finetune-lora.ipynb": notebook(n2, "Fine-tuning LoRA NLLB FR-Ewe"),
    }
    for chemin, nb in cibles.items():
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        with open(chemin, encoding="utf-8") as f:
            json.load(f)
        print("[OK]", chemin, os.path.getsize(chemin), "octets")


if __name__ == "__main__":
    main()
