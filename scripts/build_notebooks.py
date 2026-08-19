#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_notebooks.py - Genere les notebooks Colab de la Phase D :
  1. notebooks/01-baseline-nllb.ipynb   (zero-shot + evaluation)
  2. notebooks/02-finetune-lora.ipynb   (fine-tuning LoRA + comparaison)
  3. notebooks/03-eval-officielle.ipynb (scores officiels sur reference verifiee)

Conventions (regles du projet) :
  - Aucun emoji dans le code ni dans les cellules (markdown inclus).
  - Chaque bloc de code est explique en francais avant execution.
  - Les donnees sont chargees depuis le repo GitHub public
    (cherif-tg/tg_nlp_toolkit) - zero upload manuel sur Colab.
  - Cellule de diagnostic GPU en tete de chaque notebook.

ATTENTION (piege outputs) : ce script regenere les notebooks SANS leurs
outputs d'execution. Le notebook 02 commite contient les outputs reels
(scores chrF++/BLEU, logs d'entrainement) : NE PAS relancer ce script
apres avoir execute les notebooks sur Colab, sinon ces outputs seront
effaces. Pour regenerer uniquement un notebook neuf (sans outputs),
lancer le script puis restaurer les notebooks executes :
  git restore notebooks/02-finetune-lora.ipynb
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
# NOTEBOOK 1 - BASELINE NLLB (zero-shot)
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
    df = pd.read_csv(URL_TEST, sep="\\t", on_bad_lines="skip")
    print("Test set charge :", len(df), "paires FR<->Ewe")
    print(df.head(3))
except Exception as e:
    print("Telechargement GitHub impossible :", e)
    print("Solution : telecharge test.tsv depuis le repo et execute :")
    print("  from google.colab import files; upload = files.upload()")
    df = pd.read_csv("test.tsv", sep="\\t", on_bad_lines="skip")"""),

    code("""# Chargement du modele NLLB-200-distilled-600M
# 600M parametres = version "distilled" (legere), adaptee a un GPU gratuit.
MODEL_NAME = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# Verification des codes de langue (API robuste, compatible toutes versions)
# convert_tokens_to_ids renvoie l'id du token s'il existe, sinon unk_token_id.
assert tokenizer.convert_tokens_to_ids("fra_Latn") != tokenizer.unk_token_id, "francais absent"
assert tokenizer.convert_tokens_to_ids("ewe_Latn") != tokenizer.unk_token_id, "ewe absent"
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

# API moderne de sacrebleu (v2+) : sacrebleu.metrics.
from sacrebleu.metrics import CHRF, BLEU

chrf_metric = CHRF()
bleu_metric = BLEU()

# str() : se protege contre d'eventuelles valeurs non textuelles (NaN)
preds_fr_ee = traduire([str(x) for x in df["fr"].tolist()], src="fra_Latn", tgt="ewe_Latn")
refs_ee = [str(x) for x in df["ewe"].tolist()]

chrf_fr_ee = chrf_metric.corpus_score(preds_fr_ee, [refs_ee])
bleu_fr_ee = bleu_metric.corpus_score(preds_fr_ee, [refs_ee])

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
preds_ee_fr = traduire([str(x) for x in df["ewe"].tolist()], src="ewe_Latn", tgt="fra_Latn")
refs_fr = [str(x) for x in df["fr"].tolist()]

chrf_ee_fr = chrf_metric.corpus_score(preds_ee_fr, [refs_fr])
bleu_ee_fr = bleu_metric.corpus_score(preds_ee_fr, [refs_fr])

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
# NOTEBOOK 2 - FINE-TUNING LoRA
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
from sacrebleu.metrics import CHRF, BLEU
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
    return pd.read_csv(BASE + nom, sep="\\t", on_bad_lines="skip")

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
    [tokeniser([str(fr)], [str(ee)]) for fr, ee in zip(train["fr"], train["ewe"])]
)
dev_ds = Dataset.from_list(
    [tokeniser([str(fr)], [str(ee)]) for fr, ee in zip(dev["fr"], dev["ewe"])]
)
print("Datasets prets : train", len(train_ds), "| dev", len(dev_ds))
print("Exemple de cles :", list(train_ds[0].keys()))"""),

    code("""import torch  # regle les conflits de paquets sur Colab
# Configuration LoRA
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
    chrf = CHRF().corpus_score(decoded_preds, refs)
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

preds = traduire_model([str(x) for x in test["fr"].tolist()])
refs = [str(x) for x in test["ewe"].tolist()]
chrf = CHRF().corpus_score(preds, [refs])
bleu = BLEU().corpus_score(preds, [refs])

print("FR -> EWE apres fine-tuning LoRA")
print("   chrF++ :", round(chrf.score, 2), " (a comparer avec la baseline)")
print("   BLEU   :", round(bleu.score, 2))

for i in range(3):
    print("--- Exemple", i + 1, "---")
    print("FR :", test['fr'].iloc[i])
    print("Ref:", refs[i])
    print("Pred:", preds[i])"""),

    code("""# Evaluation EWE -> FR avec le modele fine-tune (comparaison complete)
def traduire_model_inverse(textes, tgt="fra_Latn", max_len=128, batch_size=16):
    tokenizer.src_lang = "ewe_Latn"
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

preds_ee_fr = traduire_model_inverse([str(x) for x in test["ewe"].tolist()])
refs_fr = [str(x) for x in test["fr"].tolist()]
chrf_ee_fr = CHRF().corpus_score(preds_ee_fr, [refs_fr])
bleu_ee_fr = BLEU().corpus_score(preds_ee_fr, [refs_fr])

print("EWE -> FR apres fine-tuning LoRA")
print("   chrF++ :", round(chrf_ee_fr.score, 2), " (a comparer avec la baseline)")
print("   BLEU   :", round(bleu_ee_fr.score, 2))"""),

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


# =========================================================================
# NOTEBOOK 3 - SCORES OFFICIELS sur le test de reference verifie
# =========================================================================
n3 = [
    md("""# 3. Scores officiels : baseline + LoRA v1 sur le test de reference verifie

**Objectif** : produire les **scores officiels** du projet en evaluant
le modele NLLB (baseline zero-shot) ET notre fine-tuning LoRA v1 sur le
**test de reference verifie a 100 %** (241 paires validees par double
verification humaine, 97 % de concordance entre verificateurs).

## Pourquoi ce notebook ?

Les scores des notebooks 1 et 2 sont mesures sur le split `test.tsv`
(6 564 paires auto-alignees, donc approximatives). Ce notebook recalcule
les scores sur la **reference verifiee** : ce sont les chiffres a publier
(dataset card, model card, memoire).

## Ce qu'on mesure

- **Baseline** : `facebook/nllb-200-distilled-600M` (zero-shot)
- **LoRA v1** : `cheriftenga/nllb-200-distilled-600M-ewe-lora` (publie sur HF)
- 2 directions : FR -> EWE et EWE -> FR, sur les 241 paires de reference.

## Metriques

- **chrF++** : metrique principale (robuste a l'orthographe historique 1913)
- **BLEU** : metrique classique (stricte, en complement)"""),

    code("""# Installation des dependances
!pip install -q transformers sacrebleu pandas sentencepiece peft accelerate

print("Dependances installees")"""),

    CELLULE_GPU,

    code("""# Imports
import torch
import pandas as pd
from sacrebleu.metrics import CHRF, BLEU
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from peft import PeftModel

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device utilise :", device)"""),

    code("""# Chargement du test de reference verifie (241 paires)
# Fichier : huggingface/test-reference-final.tsv (sep="\\t")
# Colonnes : id ; source ; fr ; ewe
URL_REF = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/huggingface/test-reference-final.tsv"

reference = pd.read_csv(URL_REF, sep="\\t", on_bad_lines="skip")
print("Reference chargee :", len(reference), "paires")
print("Repartition :", reference["source"].value_counts().to_dict())
print(reference.head(3))"""),

    md("""## Ordre d'execution

On evalue d'abord la **baseline** (modele de base NLLB), puis on la
decharge de la memoire GPU avant de charger le **LoRA v1**. Les deux
modeles font 600M de parametres : on ne peut pas les garder en memoire
en meme temps sur un T4 (16 Go)."""),

    code("""# Fonction de traduction (reutilisable pour les deux modeles)
def traduire(model, tokenizer, textes, src="fra_Latn", tgt="ewe_Latn",
             max_len=128, batch_size=16):
    tokenizer.src_lang = src
    model.eval()
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

chrf_metric = CHRF()
bleu_metric = BLEU()

def scorer(preds, refs):
    c = chrf_metric.corpus_score(preds, [refs])
    b = bleu_metric.corpus_score(preds, [refs])
    return round(c.score, 2), round(b.score, 2)

print("Fonctions pretes")"""),

    code("""# ===== 1. BASELINE (zero-shot) =====
MODEL_NAME = "facebook/nllb-200-distilled-600M"
tokenizer_base = AutoTokenizer.from_pretrained(MODEL_NAME)
model_base = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)

# Verification des codes de langue (robuste, toutes versions transformers)
assert tokenizer_base.convert_tokens_to_ids("fra_Latn") != tokenizer_base.unk_token_id
assert tokenizer_base.convert_tokens_to_ids("ewe_Latn") != tokenizer_base.unk_token_id
print("Baseline chargee")"""),

    code("""# Evaluation baseline : FR -> EWE puis EWE -> FR
fr_liste = [str(x) for x in reference["fr"].tolist()]
ew_liste = [str(x) for x in reference["ewe"].tolist()]

preds_base_fr_ee = traduire(model_base, tokenizer_base, fr_liste,
                            src="fra_Latn", tgt="ewe_Latn")
base_fr_ee = scorer(preds_base_fr_ee, ewe_liste)
print("Baseline FR->EWE : chrF++", base_fr_ee[0], "| BLEU", base_fr_ee[1])

preds_base_ee_fr = traduire(model_base, tokenizer_base, ewe_liste,
                            src="ewe_Latn", tgt="fra_Latn")
base_ee_fr = scorer(preds_base_ee_fr, fr_liste)
print("Baseline EWE->FR : chrF++", base_ee_fr[0], "| BLEU", base_ee_fr[1])"""),

    code("""# Liberation de la baseline (memoire GPU)
del model_base, tokenizer_base
torch.cuda.empty_cache()
print("Memoire GPU liberee")"""),

    code("""# ===== 2. FINE-TUNE LoRA v1 (publie sur HF) =====
# L'adaptateur LoRA seul est publie (pas le modele de base) :
# on charge le modele de base puis on applique l'adaptateur.
LORA_REPO = "cheriftenga/nllb-200-distilled-600M-ewe-lora"
BASE = "facebook/nllb-200-distilled-600M"

base_model = AutoModelForSeq2SeqLM.from_pretrained(BASE)
model_lora = PeftModel.from_pretrained(base_model, LORA_REPO).to(device)
tokenizer_lora = AutoTokenizer.from_pretrained(LORA_REPO)
print("LoRA v1 charge depuis HuggingFace")"""),

    code("""# Evaluation LoRA v1 : FR -> EWE puis EWE -> FR
preds_lora_fr_ee = traduire(model_lora, tokenizer_lora, fr_liste,
                            src="fra_Latn", tgt="ewe_Latn")
lora_fr_ee = scorer(preds_lora_fr_ee, ewe_liste)
print("LoRA v1 FR->EWE : chrF++", lora_fr_ee[0], "| BLEU", lora_fr_ee[1])

preds_lora_ee_fr = traduire(model_lora, tokenizer_lora, ewe_liste,
                            src="ewe_Latn", tgt="fra_Latn")
lora_ee_fr = scorer(preds_lora_ee_fr, fr_liste)
print("LoRA v1 EWE->FR : chrF++", lora_ee_fr[0], "| BLEU", lora_ee_fr[1])"""),

    code("""# ===== 3. Tableau comparatif officiel + sauvegarde =====
resume = pd.DataFrame({
    "Direction": ["FR->EWE", "FR->EWE", "EWE->FR", "EWE->FR"],
    "Modele": ["Baseline", "LoRA v1", "Baseline", "LoRA v1"],
    "chrF++": [base_fr_ee[0], lora_fr_ee[0], base_ee_fr[0], lora_ee_fr[0]],
    "BLEU": [base_fr_ee[1], lora_fr_ee[1], base_ee_fr[1], lora_ee_fr[1]],
})
print("=== SCORES OFFICIELS (test de reference verifie, 241 paires) ===")
print(resume.to_string(index=False))

# Sauvegarde des predictions detaillees (utile pour le benchmark Google
# Translate et pour l'analyse d'erreurs)
resultats = pd.DataFrame({
    "id": reference["id"],
    "source": reference["source"],
    "fr": reference["fr"],
    "ewe": reference["ewe"],
    "pred_fr_ee": preds_lora_fr_ee,
    "pred_ee_fr": preds_lora_ee_fr,
})
resultats.to_csv("scores-officiels-predictions.csv", index=False, sep=";")
resume.to_csv("scores-officiels-resume.csv", index=False, sep=";")
print("Fichiers sauvegardes : scores-officiels-predictions.csv, scores-officiels-resume.csv")"""),

    md("""## Lecture des resultats

- **FR->EWE** : on attend le gain LoRA (environ +7 chrF++ par rapport a la
  baseline, comme sur le split auto-aligne).
- **EWE->FR** : c'est le sens faible (le modele v1 n'a ete entraine que sur
  FR->EWE). Le fine-tuning v2 (bidirectionnel) vise a le corriger.
- Ces scores remplacent les chiffres approximatifs des notebooks 1 et 2 :
  reporte-les dans la model card et le README.

**Prochaines etapes** :
1. Benchmark Google Translate sur ces memes 241 paires (comparaison)
2. Fine-tuning v2 bidirectionnel (notebook 02b) pour ameliorer EWE->FR
3. Mise a jour de la model card avec ces scores officiels"""),
]


# =========================================================================
# NOTEBOOK 2b — FINE-TUNING LoRA v2 (bidirectionnel)
# =========================================================================
n2b = [
    md("""# 2b. Fine-tuning v2 : bidirectionnel FR <-> EWE

**Objectif** : corriger le point faible de la v1. La v1 (entrainee
uniquement FR -> EWE) a fait progresser FR -> EWE (+10,17 chrF++ officiels)
mais pas EWE -> FR (stagnation a 37,52).

## Principe du bidirectionnel

On **double le jeu d'entrainement en inversant les paires** :

```
exemple 1 : fr  -> ewe   (source = francais, labels = ewe)
exemple 2 : ewe -> fr    (source = ewe, labels = francais)  <- inverse
```

- Train : 2 x 52 512 = **105 024 paires**
- Dev   : 2 x 6 564  = 13 128 paires
- Le modele apprend a la fois a COMPRENDRE et a PRODUIRE chaque langue
  (standard pour un traducteur bidirectionnel, comme NLLB lui-meme).

## Objectifs (scores officiels sur reference verifiee, 241 paires)

| Direction | Baseline | v1 | v2 (attendu) |
|---|---|---|---|
| FR -> EWE | 37,22 | 47,39 | >= 41 (ne pas perdre) |
| EWE -> FR | 38,14 | 37,52 | **>= 37** (viser 40) |

## Pipeline

1. Charger train/dev depuis GitHub
2. Construire le dataset bidirectionnel (tokenisation par exemple)
3. LoRA (memes hyperparametres que v1 : r=16, alpha=32)
4. Entrainer (~60-90 min sur T4)
5. Evaluer les 2 directions sur la reference verifiee et comparer"""),

    code("""# Installation
!pip install -q transformers sacrebleu pandas sentencepiece datasets peft accelerate

print("Dependances installees")"""),

    CELLULE_GPU,

    code("""# Imports
import torch
import pandas as pd
from sacrebleu.metrics import CHRF, BLEU
import numpy as np
from transformers import (AutoTokenizer, AutoModelForSeq2SeqLM,
                          Seq2SeqTrainer, Seq2SeqTrainingArguments,
                          DataCollatorForSeq2Seq)
from datasets import Dataset
from peft import LoraConfig, get_peft_model

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device utilise :", device)"""),

    code("""# Chargement train / dev depuis le repo GitHub public
BASE = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/data/processed/v0.3/"

def charger(nom):
    return pd.read_csv(BASE + nom, sep="\\t", on_bad_lines="skip")

train = charger("train.tsv")
dev   = charger("dev.tsv")
print("train =", len(train), "| dev =", len(dev))
print(train.head(2))"""),

    code("""# Chargement du modele + tokenizer (avant la tokenisation)
MODEL_NAME = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME).to(device)
model.config.use_cache = False  # requis par le Trainer
print("Modele charge")"""),

    md("""## Tokenisation par exemple (bidirectionnelle)

Contrainte NLLB : `tokenizer.src_lang` doit etre la langue SOURCE de chaque
exemple. En v1 on fixait une seule direction ; en v2, chaque exemple porte
sa propre direction (source, cible, code_src, code_tgt)."""),

    code("""# Construction du dataset bidirectionnel
# Chaque paire produit DEUX exemples : fr->ewe et ewe->fr.
def tokeniser_exemple(source, cible, code_src, code_tgt):
    tokenizer.src_lang = code_src
    enc = tokenizer(source, max_length=128, truncation=True,
                    return_tensors="pt")
    tokenizer.src_lang = code_tgt
    labels = tokenizer(cible, max_length=128, truncation=True,
                       return_tensors="pt")
    enc["labels"] = labels["input_ids"].clone()
    # -100 = tokens ignores par la loss (padding)
    enc["labels"][enc["labels"] == tokenizer.pad_token_id] = -100
    return {k: v.numpy() for k, v in enc.items()}

# Tuple : (source, cible, code_src, code_tgt)
paires_train = []
for fr, ee in zip(train["fr"].astype(str), train["ewe"].astype(str)):
    paires_train.append((fr, ee, "fra_Latn", "ewe_Latn"))  # fr -> ewe
    paires_train.append((ee, fr, "ewe_Latn", "fra_Latn"))  # ewe -> fr

paires_dev = []
for fr, ee in zip(dev["fr"].astype(str), dev["ewe"].astype(str)):
    paires_dev.append((fr, ee, "fra_Latn", "ewe_Latn"))
    paires_dev.append((ee, fr, "ewe_Latn", "fra_Latn"))

print("Construction du train (peut prendre quelques minutes)...")
train_ds = Dataset.from_list(
    [tokeniser_exemple(s, c, a, b) for (s, c, a, b) in paires_train]
)
print("Construction du dev...")
dev_ds = Dataset.from_list(
    [tokeniser_exemple(s, c, a, b) for (s, c, a, b) in paires_dev]
)
print("Datasets prets : train", len(train_ds), "| dev", len(dev_ds))
print("Exemple de cles :", list(train_ds[0].keys()))"""),

    code("""import torch  # regle les conflits de paquets sur Colab
# Configuration LoRA (identique a la v1)
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="SEQ_2_SEQ_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Attendu : ~0,5 % des parametres entrainables"""),

    code("""# Metrique d'evaluation pendant l'entrainement : chrF++ sur le dev set
def compute_metrics(eval_pred):
    preds, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    refs = [[r] for r in decoded_labels]
    chrf = CHRF().corpus_score(decoded_preds, refs)
    return {"chrF++": chrf.score}

collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
print("Metrique + collator prets")"""),

    code("""# Configuration de l'entrainement (identique a la v1)
training_args = Seq2SeqTrainingArguments(
    output_dir="nllb-ewe-lora-v2",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=3e-4,
    warmup_steps=200,
    weight_decay=0.01,
    logging_steps=100,                # plus de logs (2x plus de donnees)
    eval_strategy="epoch",
    save_strategy="epoch",
    predict_with_generate=True,
    generation_max_length=128,
    fp16=True,
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

print("Trainer pret - lance l'entrainement (~60-90 min sur T4)")"""),

    code("""# LANCEMENT DE L'ENTRAINEMENT (~60-90 min sur T4)
trainer.train()

print("Entrainement termine !")"""),

    code("""# Chargement du test de reference verifie (241 paires)
URL_REF = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/huggingface/test-reference-final.tsv"
reference = pd.read_csv(URL_REF, sep="\\t", on_bad_lines="skip")
print("Reference chargee :", len(reference), "paires")

fr_liste = [str(x) for x in reference["fr"].tolist()]
ew_liste = [str(x) for x in reference["ewe"].tolist()]

# Fonction de traduction (reutilisable dans les deux directions)
def traduire(textes, src="fra_Latn", tgt="ewe_Latn", max_len=128, batch_size=16):
    tokenizer.src_lang = src
    model.eval()
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

    code("""# Evaluation v2 : FR -> EWE puis EWE -> FR (sur la reference verifiee)
chrf_metric = CHRF()
bleu_metric = BLEU()

def scorer(preds, refs):
    c = chrf_metric.corpus_score(preds, [refs])
    b = bleu_metric.corpus_score(preds, [refs])
    return round(c.score, 2), round(b.score, 2)

preds_fr_ee = traduire(fr_liste, src="fra_Latn", tgt="ewe_Latn")
v2_fr_ee = scorer(preds_fr_ee, ewe_liste)
print("v2 FR->EWE : chrF++", v2_fr_ee[0], "| BLEU", v2_fr_ee[1])

preds_ee_fr = traduire(ewe_liste, src="ewe_Latn", tgt="fra_Latn")
v2_ee_fr = scorer(preds_ee_fr, fr_liste)
print("v2 EWE->FR : chrF++", v2_ee_fr[0], "| BLEU", v2_ee_fr[1])"""),

    code("""# Tableau comparatif baseline / v1 / v2 (scores officiels, 241 paires)
resume = pd.DataFrame({
    "Direction": ["FR->EWE", "FR->EWE", "FR->EWE",
                  "EWE->FR", "EWE->FR", "EWE->FR"],
    "Modele": ["Baseline", "LoRA v1", "LoRA v2",
               "Baseline", "LoRA v1", "LoRA v2"],
    "chrF++": [37.22, 47.39, v2_fr_ee[0], 38.14, 37.52, v2_ee_fr[0]],
    "BLEU": [11.17, 22.20, v2_fr_ee[1], 14.92, 15.15, v2_ee_fr[1]],
})
print("=== COMPARAISON OFFICIELLE (reference verifiee, 241 paires) ===")
print(resume.to_string(index=False))

# Objectifs v2
obj_ee_fr = v2_ee_fr[0] >= 37
obj_fr_ee = v2_fr_ee[0] >= 41
print("\\nObjectif EWE->FR >= 37 :", "ATTEINT" if obj_ee_fr else "NON atteint")
print("Objectif FR->EWE >= 41 (ne pas perdre) :", "ATTEINT" if obj_fr_ee else "NON atteint")

# Sauvegarde des predictions + scores
resultats = pd.DataFrame({
    "id": reference["id"],
    "source": reference["source"],
    "fr": reference["fr"],
    "ewe": reference["ewe"],
    "pred_fr_ee": preds_fr_ee,
    "pred_ee_fr": preds_ee_fr,
})
resultats.to_csv("v2-predictions.csv", index=False, sep=";")
resume.to_csv("v2-scores.csv", index=False, sep=";")
print("Fichiers sauvegardes : v2-predictions.csv, v2-scores.csv")"""),

    code("""# Export du modele v2 vers HuggingFace (apres connexion)
# Decommente et execute APRES t'etre connecte :
#   from huggingface_hub import notebook_login
#   notebook_login()   # colle ton token
#
#   model.push_to_hub("cheriftenga/nllb-200-distilled-600M-ewe-lora-v2")
#   tokenizer.push_to_hub("cheriftenga/nllb-200-distilled-600M-ewe-lora-v2")
print("Pret pour l'export (voir instructions commentees)")"""),

    md("""## Lecture des resultats

- **EWE -> FR >= 37** : objectif atteint, le bidirectionnel a corrige le
  point faible de la v1. Publie le modele v2.
- **FR -> EWE < 41** (perte du gain v1) : parade du plan v2 =
  repasser en unidirectionnel ou augmenter la proportion de paires
  fr->ewe (ex. 2/3 - 1/3).
- Rapporte les 4 chiffres affiches pour mettre a jour la model card et
  les docs de resultats.

**Prochaines etapes** : benchmark Google Translate (241 paires), MTPE
interne (grilles sante/administration), phase audio (ASR)."""),
]


# =========================================================================
# NOTEBOOK 4 — BENCHMARK GOOGLE TRANSLATE
# =========================================================================
n4 = [
    md("""# 4. Benchmark : notre modele vs Google Translate

**Objectif** : comparer notre meilleur modele (LoRA v2) a Google Translate
sur les 241 paires du test de reference verifie.

## Pourquoi ?

- Google Translate couvre l'ewe depuis mai 2022.
- Comparer nos scores a ceux de Google situe notre modele : est-il
  competitif avec un geant commercial ?
- Resultat parlant pour le memoire (\"notre modele vs Google Translate\").

## Methode

1. Traduire les 241 paires avec Google Translate (les 2 directions)
2. Calculer chrF++ / BLEU (meme metrique que pour nos modeles)
3. Comparer : baseline / v1 / v2 / Google Translate

## Avertissements

- On utilise la bibliotheque `googletrans` (acces NON officiel a l'API web
  de Google). Elle peut etre fragile (rate limit, changements d'API).
  Si elle echoue : alternative = `deep-translator` ou l'API officielle
  Google Cloud (cle gratuite, quota 500k caracteres/mois).
- Les traductions Google ne sont JAMAIS injectees dans notre corpus
  (CGU Google + contamination).
- Pas besoin de GPU : ce notebook tourne sur CPU."""),

    code("""# Installation
!pip install -q googletrans==4.0.0rc1 sacrebleu pandas

print("Dependances installees")"""),

    code("""# Imports
import time
import pandas as pd
from sacrebleu.metrics import CHRF, BLEU
from googletrans import Translator

translator = Translator()
print("Pret (execution sur CPU, pas besoin de GPU)")"""),

    code("""# Chargement du test de reference verifie (241 paires)
URL_REF = "https://raw.githubusercontent.com/cherif-tg/tg_nlp_toolkit/main/huggingface/test-reference-final.tsv"
reference = pd.read_csv(URL_REF, sep="\\t", on_bad_lines="skip")
print("Reference chargee :", len(reference), "paires")

fr_liste = [str(x) for x in reference["fr"].tolist()]
ew_liste = [str(x) for x in reference["ewe"].tolist()]"""),

    code("""# Traduction via Google Translate (retries + pause anti rate-limit)
def traduire_gt(textes, src, dest, pause=0.4):
    resultats = []
    for i, t in enumerate(textes):
        ok = False
        for tentative in range(4):
            try:
                r = translator.translate(t, src=src, dest=dest)
                resultats.append(r.text)
                ok = True
                break
            except Exception as e:
                time.sleep(1.5 * (tentative + 1))
        if not ok:
            resultats.append("")
            print(f"  echec ligne {i}: {t[:40]}")
        time.sleep(pause)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(textes)}")
    return resultats

print("Fonction de traduction Google prete")"""),

    code("""# Traduction FR -> EWE via Google Translate (code Google : ee)
print("Traduction FR -> EWE (241 paires)...")
gt_fr_ee = traduire_gt(fr_liste, src="fr", dest="ee")
print("Termine. Exemple :")
print("  FR :", fr_liste[0])
print("  GT :", gt_fr_ee[0])
print("  Ref:", ewe_liste[0])"""),

    code("""# Traduction EWE -> FR via Google Translate
print("Traduction EWE -> FR (241 paires)...")
gt_ee_fr = traduire_gt(ewe_liste, src="ee", dest="fr")
print("Termine. Exemple :")
print("  EWE :", ewe_liste[0])
print("  GT  :", gt_ee_fr[0])
print("  Ref :", fr_liste[0])"""),

    code("""# Calcul des scores Google (chrF++ / BLEU)
chrf_metric = CHRF()
bleu_metric = BLEU()

def scorer(preds, refs):
    c = chrf_metric.corpus_score(preds, [refs])
    b = bleu_metric.corpus_score(preds, [refs])
    return round(c.score, 2), round(b.score, 2)

# Filtrer les traductions vides (echecs googletrans)
valides_fr_ee = [(p, r) for p, r in zip(gt_fr_ee, ewe_liste) if p.strip()]
valides_ee_fr = [(p, r) for p, r in zip(gt_ee_fr, fr_liste) if p.strip()]
print(f"FR->EWE : {len(valides_fr_ee)}/{len(gt_fr_ee)} traductions reussies")
print(f"EWE->FR : {len(valides_ee_fr)}/{len(gt_ee_fr)} traductions reussies")

gt_fr_ee_score = scorer([p for p, _ in valides_fr_ee], [r for _, r in valides_fr_ee])
gt_ee_fr_score = scorer([p for p, _ in valides_ee_fr], [r for _, r in valides_ee_fr])
print("Google FR->EWE : chrF++", gt_fr_ee_score[0], "| BLEU", gt_fr_ee_score[1])
print("Google EWE->FR : chrF++", gt_ee_fr_score[0], "| BLEU", gt_ee_fr_score[1])"""),

    code("""# Tableau comparatif complet (baseline / v1 / v2 / Google)
resume = pd.DataFrame({
    "Direction": ["FR->EWE"] * 4 + ["EWE->FR"] * 4,
    "Modele": ["Baseline", "LoRA v1", "LoRA v2", "Google Translate",
               "Baseline", "LoRA v1", "LoRA v2", "Google Translate"],
    "chrF++": [37.22, 47.39, 47.95, gt_fr_ee_score[0],
               38.14, 37.52, 52.24, gt_ee_fr_score[0]],
    "BLEU": [11.17, 22.20, 22.42, gt_fr_ee_score[1],
             14.92, 15.15, 31.83, gt_ee_fr_score[1]],
})
print("=== BENCHMARK : notre modele vs Google Translate (241 paires) ===")
print(resume.to_string(index=False))

# Sauvegarde
resume.to_csv("benchmark-google.csv", index=False, sep=";")
print("Sauvegarde : benchmark-google.csv")"""),

    md("""## Lecture des resultats

- Si notre v2 >= Google Translate : notre modele est competitif avec un
  geant commercial sur ce domaine (biblique/generaliste) - argument fort.
- Si Google domine : normal (donnees massives + ewe moderne). Notre valeur
  = open-source, hors-ligne, adapte a l'ewe du Togo, et le kabiyè (que
  Google ne couvre pas).
- Rapporte le tableau pour le memoire et la mise a jour des docs."""),
]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Genere les notebooks Colab")
    parser.add_argument("--only", help="Genere uniquement ce notebook (ex. 02b)")
    args = parser.parse_args()

    os.makedirs("notebooks", exist_ok=True)
    cibles = {
        "notebooks/01-baseline-nllb.ipynb": notebook(n1, "Baseline NLLB FR-Ewe"),
        "notebooks/02-finetune-lora.ipynb": notebook(n2, "Fine-tuning LoRA NLLB FR-Ewe"),
        "notebooks/02b-finetune-lora-v2.ipynb": notebook(n2b, "Fine-tuning LoRA v2 bidirectionnel FR-EWE"),
        "notebooks/03-eval-officielle.ipynb": notebook(n3, "Scores officiels sur reference verifiee"),
        "notebooks/04-benchmark-google-translate.ipynb": notebook(n4, "Benchmark Google Translate vs notre modele"),
    }
    if args.only:
        cibles = {k: v for k, v in cibles.items() if args.only in k}
        if not cibles:
            print("Notebook inconnu :", args.only)
            return
    for chemin, nb in cibles.items():
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        with open(chemin, encoding="utf-8") as f:
            json.load(f)
        print("[OK]", chemin, os.path.getsize(chemin), "octets")


if __name__ == "__main__":
    main()
