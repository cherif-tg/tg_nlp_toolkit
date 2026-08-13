#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_notebooks.py — Génère les notebooks Colab de la Phase D :
  1. notebooks/01-baseline-nllb.ipynb        (zero-shot + évaluation)
  2. notebooks/02-finetune-lora.ipynb        (fine-tuning LoRA + comparaison)

Le contenu est pédagogique : chaque bloc de code est précédé d'explications
en français. Les données sont chargées directement depuis le repo GitHub
public (cherif-tg/tg_nlp_toolkit) — zéro upload manuel sur Colab.
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


# =========================================================================
# NOTEBOOK 1 — BASELINE NLLB (zero-shot)
# =========================================================================
n1 = [
    md("""# 1. Baseline : NLLB-200 (zero-shot) FR ↔ Éwé

**Objectif** : mesurer la qualité de traduction du modèle **NLLB-200-distilled-600M**
(Meta AI) sur notre corpus de test **sans aucun entraînement** (mode "zero-shot").

C'est la **référence de départ** : tout le travail de fine-tuning (notebook 2)
devra faire mieux que ces scores.

## Comment ça marche ?

- **NLLB** ("No Language Left Behind") est un modèle de traduction multilingue
  entraîné sur 200 langues, dont l'**éwé** (code `ewe_Latn`).
- Il est **"zero-shot"** pour nous : il n'a jamais vu notre corpus, mais il a vu
  de l'éwé pendant son entraînement.
- On mesure la qualité avec deux métriques standard :
  - **chrF++** (la métrique principale du projet, robuste aux petites variations)
  - **BLEU** (métrique classique, plus stricte)

> ⚠️ Le test set est chargé depuis le **repo GitHub public** du projet.
> C'est le split `test.tsv` : 1 898 paires jamais utilisées pour l'entraînement."""),

    code("""# Installation des bibliothèques nécessaires
# - transformers : modèles HuggingFace (NLLB)
# - sacrebleu    : métriques chrF++ et BLEU
# - pandas       : lecture des fichiers TSV
# - sentencepiece : tokenizer de NLLB (obligatoire)
!pip install -q transformers sacrebleu pandas sentencepiece datasets

print("✅ Dépendances installées")"""),

    code("""# Imports + détection du GPU
import torch
import pandas as pd
import sacrebleu
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Colab met un GPU (T4) à disposition : on l'utilise si disponible.
device = "cuda" if torch.cuda.is_available() else "cpu"
print("🔧 Device utilisé :", device)
print("   (cuda = GPU, cpu = lent mais fonctionne)")"""),

    code("""# Chargement du jeu de test depuis le repo GitHub public
# Les données du projet sont versionnées : ce notebook charge la version "main".
URL_TEST = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/data/processed/v0.1/test.tsv"

try:
    df = pd.read_csv(URL_TEST, sep="\\t")
    print(f"✅ Test set chargé : {len(df)} paires FR↔Éwé")
    print(df.head(3))
except Exception as e:
    print("❌ Téléchargement GitHub impossible :", e)
    print("→ Solution : télécharge test.tsv depuis le repo et exécute cette cellule :")
    print("   from google.colab import files; upload = files.upload()")"""),

    code("""# Chargement du modèle NLLB-200-distilled-600M
# 600M paramètres = version "distilled" (légère), parfaite pour un GPU gratuit.
MODEL_NAME = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# Vérification : les codes de langue existent-ils ?
assert "fra_Latn" in tokenizer.additional_special_tokens, "français absent ?!"
assert "ewe_Latn" in tokenizer.additional_special_tokens, "éwé absent ?!"
print("✅ Modèle chargé — codes langue : fra_Latn (fr), ewe_Latn (éwé)")"""),

    code("""# Fonction de traduction en batch
# - src / tgt : codes de langue NLLB (fra_Latn, ewe_Latn)
# - num_beams=4 : recherche en faisceau (meilleure qualité que greedy)
# - Le tokenizer doit connaître la langue SOURCE avant d'encoder.

def traduire(textes, src="fra_Latn", tgt="ewe_Latn", max_len=128, batch_size=16):
    tokenizer.src_lang = src          # langue source pour l'encodage
    resultats = []
    for i in range(0, len(textes), batch_size):
        lot = textes[i:i + batch_size]
        enc = tokenizer(lot, return_tensors="pt", padding=True,
                        truncation=True, max_length=max_len).to(device)
        with torch.no_grad():
            gen = model.generate(
                **enc,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt),  # langue cible
                max_new_tokens=max_len,
                num_beams=4,
            )
        resultats += tokenizer.batch_decode(gen, skip_special_tokens=True)
    return resultats

print("✅ Fonction de traduction prête")"""),

    code("""# Évaluation FR → ÉWÉ (le sens qui nous intéresse le plus)
# On traduit les 1 898 phrases françaises du test set, puis on compare
# aux traductions éwé de référence avec chrF++ et BLEU.

preds_fr_ee = traduire(df["fr"].tolist(), src="fra_Latn", tgt="ewe_Latn")
refs_ee = df["ewe"].tolist()

chrf_fr_ee = sacrebleu.corpus.chrf(preds_fr_ee, [refs_ee])
bleu_fr_ee = sacrebleu.corpus.bleu(preds_fr_ee, [refs_ee])

print("📊 FR → ÉWÉ (zero-shot)")
print(f"   chrF++ : {chrf_fr_ee.score:.2f}")
print(f"   BLEU   : {bleu_fr_ee.score:.2f}")

# Afficher 3 exemples concrets pour voir la qualité à l'œil
for i in range(3):
    print(f"\\n--- Exemple {i+1} ---")
    print(f"FR : {df['fr'].iloc[i]}")
    print(f"Réf: {refs_ee[i]}")
    print(f"Préd: {preds_fr_ee[i]}")"""),

    code("""# Évaluation ÉWÉ → FR (sens inverse)
# Utile pour vérifier que le modèle comprend aussi l'éwé en entrée.

preds_ee_fr = traduire(df["ewe"].tolist(), src="ewe_Latn", tgt="fra_Latn")
refs_fr = df["fr"].tolist()

chrf_ee_fr = sacrebleu.corpus.chrf(preds_ee_fr, [refs_fr])
bleu_ee_fr = sacrebleu.corpus.bleu(preds_ee_fr, [refs_fr])

print("📊 ÉWÉ → FR (zero-shot)")
print(f"   chrF++ : {chrf_ee_fr.score:.2f}")
print(f"   BLEU   : {bleu_ee_fr.score:.2f}")

print("\\n📋 Tableau de bord baseline :")
print(f"   FR→ÉWÉ : chrF++ {chrf_fr_ee.score:.2f} | BLEU {bleu_fr_ee.score:.2f}")
print(f"   ÉWÉ→FR : chrF++ {chrf_ee_fr.score:.2f} | BLEU {bleu_ee_fr.score:.2f}")"""),

    md("""## Comment interpréter ces scores ?

- **chrF++ ~40-55** sur cette tâche = le modèle "se débrouille" (vocabulaire
  religieux bien connu de NLLB, car la bible fait partie de ses données).
- **BLEU bas (< 15)** est normal : BLEU est très strict sur les mots exacts,
  et l'éwé de 1913 a une orthographe différente de l'éwé moderne vu par NLLB.
- Ces scores sont notre **référence** : le notebook 2 (fine-tuning LoRA sur
  notre corpus) doit les **dépasser**, surtout en chrF++.

> 💡 Si le score est très bas, vérifie que le GPU est actif
> (menu *Exécution > Changer le type d'exécution > T4 GPU*)."""),
]

# =========================================================================
# NOTEBOOK 2 — FINE-TUNING LoRA
# =========================================================================
n2 = [
    md("""# 2. Fine-tuning de NLLB avec LoRA sur notre corpus

**Objectif** : adapter NLLB-200-distilled-600M à NOTRE corpus (éwé de 1913 +
segond 1910) avec **LoRA** (Low-Rank Adaptation), pour dépasser la baseline.

## Pourquoi LoRA et pas un fine-tuning complet ?

- Un fine-tuning complet modifierait les **600M de paramètres** → GPU saturé,
  heures d'entraînement, risques d'oubli catastrophique.
- **LoRA** ne modifie que de petits "adaptateurs" (~0,5 % des paramètres)
  ajoutés aux couches d'attention : rapide, léger, et le modèle de base reste
  intact.
- Résultat : ~10-20 min d'entraînement sur un T4 gratuit pour 3 époques.

## Pipeline

1. Charger `train.tsv` (15 199 paires) et `dev.tsv` (1 898 paires) depuis GitHub
2. Tokeniser les paires (langue source + langue cible NLLB)
3. Ajouter les adaptateurs LoRA
4. Entraîner avec `Seq2SeqTrainer` (HuggingFace)
5. Évaluer sur `test.tsv` et **comparer avec la baseline** (notebook 1)"""),

    code("""# Installation (peft = bibliothèque officielle LoRA de HuggingFace)
!pip install -q transformers sacrebleu pandas sentencepiece datasets peft accelerate

print("✅ Dépendances installées")"""),

    code("""# Imports + GPU
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
print("🔧 Device :", device)
# Sur Colab : Exécution > Changer le type d'exécution > T4 GPU"""),

    code("""# Chargement train / dev / test depuis le repo GitHub public
BASE = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/data/processed/v0.1/"

def charger(nom):
    return pd.read_csv(BASE + nom, sep="\\t")

train = charger("train.tsv")
dev   = charger("dev.tsv")
test  = charger("test.tsv")
print(f"✅ train={len(train)} dev={len(dev)} test={len(test)}")
print(train.head(2))"""),

    code("""# Chargement du modèle + tokenizer
MODEL_NAME = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# On gèle le modèle de base : seuls les adaptateurs LoRA seront entraînés
model.config.use_cache = False   # requis par le Trainer pendant l'entraînement
print("✅ Modèle chargé")"""),

    code("""# Préparation des données au format attendu par le Trainer
# Chaque exemple : "input" = phrase source (préfixée par la langue), "labels" = cible

def preparer(df, src_lang, tgt_lang):
    # Le tokenizer NLLB ajoute automatiquement le préfixe de langue si on
    # fixe src_lang AVANT l'encodage, et forced_bos_token_id à la génération.
    sources, cibles = [], []
    for fr, ee in zip(df["fr"], df["ewe"]):
        sources.append(fr)
        cibles.append(ee)
    return sources, cibles

train_src, train_tgt = preparer(train, "fra_Latn", "ewe_Latn")
dev_src, dev_tgt     = preparer(dev, "fra_Latn", "ewe_Latn")

# Encodage : les entrées sont tokenisées avec la langue source,
# les labels avec la langue cible (pad_token = label -100 pour ignorer le padding)
def tokeniser(sources, cibles):
    tokenizer.src_lang = "fra_Latn"
    enc = tokenizer(sources, padding=True, truncation=True, max_length=128, return_tensors="pt")
    tokenizer.src_lang = "ewe_Latn"
    labels = tokenizer(cibles, padding=True, truncation=True, max_length=128, return_tensors="pt")
    enc["labels"] = labels["input_ids"]
    # -100 = tokens ignorés par la loss (padding)
    enc["labels"][enc["labels"] == tokenizer.pad_token_id] = -100
    return enc

train_ds = Dataset.from_dict(tokeniser(train_src, train_tgt))
dev_ds   = Dataset.from_dict(tokeniser(dev_src, dev_tgt))
print(f"✅ Datasets prêts : train {len(train_ds)} exemples, dev {len(dev_ds)}")"""),

    code("""# Configuration LoRA
# On ajoute des adaptateurs sur les projections Q et V de l'attention
# (cible classique pour les modèles seq2seq).
lora_config = LoraConfig(
    r=16,                # rang de la factorisation (plus = plus de capacité)
    lora_alpha=32,       # échelle de mise à jour (souvent 2×r)
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,   # régularisation
    bias="none",
    task_type="SEQ_2_SEQ_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Attendu : ~0,5 % des paramètres entraînables seulement !"""),

    code("""# Métrique d'évaluation pendant l'entraînement : chrF++ sur le dev set
def compute_metrics(eval_pred):
    preds, labels = eval_pred
    # On décode les prédictions et les labels (en ignorant les -100)
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    # SacreBLEU attend une liste de références par phrase
    refs = [[r] for r in decoded_labels]
    chrf = sacrebleu.corpus.chrf(decoded_preds, refs)
    return {"chrF++": chrf.score}

collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
print("✅ Métrique + collator prêts")"""),

    code("""# Configuration de l'entraînement (adaptée à un T4 gratuit)
training_args = Seq2SeqTrainingArguments(
    output_dir="nllb-ewe-lora",
    num_train_epochs=3,          # 3 passages sur le corpus
    per_device_train_batch_size=8,   # 8 paires par lot (T4 ≈ 16 Go)
    per_device_eval_batch_size=8,
    learning_rate=3e-4,
    warmup_steps=200,
    weight_decay=0.01,
    logging_steps=50,
    eval_strategy="epoch",       # évaluer à chaque fin d'époque
    save_strategy="epoch",
    predict_with_generate=True,  # génère de vraies traductions pour la métrique
    generation_max_length=128,
    fp16=True,                   # demi-précision : +rapide sur T4
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

print("✅ Trainer prêt — lance l'entraînement avec la cellule suivante")"""),

    code("""# 🚀 LANCEMENT DE L'ENTRAÎNEMENT (~10-20 min sur T4)
trainer.train()

print("✅ Entraînement terminé !")"""),

    code("""# Évaluation finale sur le TEST set (jamais vu par le modèle)
# On compare avec la baseline du notebook 1.

def traduire_model(textes, tgt="ewe_Latn", max_len=128, batch_size=16):
    tokenizer.src_lang = "fra_Latn"
    resultats = []
    for i in range(0, len(textes), batch_size):
        lot = textes[i:i + batch_size]
        enc = tokenizer(lot, return_tensors="pt", padding=True,
                        truncation=True, max_length=max_len).to(device)
        with torch.no_grad():
            gen = model.generate(**enc,
                                 forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt),
                                 max_new_tokens=max_len, num_beams=4)
        resultats += tokenizer.batch_decode(gen, skip_special_tokens=True)
    return resultats

preds = traduire_model(test["fr"].tolist())
refs  = test["ewe"].tolist()
chrf = sacrebleu.corpus.chrf(preds, [refs])
bleu = sacrebleu.corpus.bleu(preds, [refs])

print("📊 FR → ÉWÉ après fine-tuning LoRA")
print(f"   chrF++ : {chrf.score:.2f}   (baseline zero-shot à comparer)")
print(f"   BLEU   : {bleu.score:.2f}")

for i in range(3):
    print(f"\\n--- Exemple {i+1} ---")
    print(f"FR : {test['fr'].iloc[i]}")
    print(f"Réf: {refs[i]}")
    print(f"Préd: {preds[i]}")"""),

    code("""# Sauvegarde du modèle + export vers HuggingFace (optionnel)
# 1) Sauvegarde locale (dossier modèle complet)
model.save_pretrained("nllb-ewe-lora-final")
tokenizer.save_pretrained("nllb-ewe-lora-final")
print("✅ Modèle sauvegardé dans nllb-ewe-lora-final/")

# 2) Export vers ton compte HuggingFace (cheriftenga)
# Décommente et exécute APRÈS t'être connecté :
#   from huggingface_hub import notebook_login
#   notebook_login()   # colle ton token (réglages > Access Tokens)
#
#   from peft import PeftModel
#   model.push_to_hub("cheriftenga/nllb-200-distilled-600M-ewe-lora")
#   tokenizer.push_to_hub("cheriftenga/nllb-200-distilled-600M-ewe-lora")
print("✅ Prêt pour l'export (voir instructions commentées)")"""),

    md("""## Lecture des résultats

- Si **chrF++ fine-tune > chrF++ baseline** (notebook 1) : notre corpus apporte
  un vrai gain → le corpus v0.1 est **utile et publiable**.
- Si le gain est faible : vérifier (a) le nombre d'époques, (b) le `r` de LoRA,
  (c) la taille du corpus. Les données restent la contrainte principale en
  low-resource.

**Prochaines étapes** : démo Gradio (P3), publication HuggingFace,
puis traduction manuelle des grilles (10 thèmes) pour couvrir le domaine
santé/administration."""),
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
        # validation : le JSON doit se relire
        with open(chemin, encoding="utf-8") as f:
            json.load(f)
        print(f"[OK] {chemin} ({os.path.getsize(chemin)} octets)")


if __name__ == "__main__":
    main()
