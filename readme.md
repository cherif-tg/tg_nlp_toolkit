# Kabiyè-Éwé NLP Toolkit

Toolkit NLP open-source pour les langues togolaises : traduction automatique
**français ↔ éwé** (objectif principal), extension **kabiyè** prévue, ASR
conditionnel en phase finale.

## Corpus

Corpus parallèle **FR↔Éwé v0.2** : **16 050 paires** (train 12 844 / dev 1 603 /
test 1 603), alignées depuis deux sources domaine public :

- Bible éwé 1913 (BFBS) — OCR normalisé (66 livres, 25 581 versets)
- Bible Segond 1910 — 31 170 versets

**Statut** : exploratoire. Qualité estimée ~66 % de paires correctes sur un
échantillon de 100 paires vérifié par un locuteur natif — voir la
[datasheet](data/processed/v0.2/DATASHEET.md) pour le détail et les biais connus.

## Utilisation

### 1. Entraînement (Google Colab)

| Notebook | Contenu |
|---|---|
| [`01-baseline-nllb.ipynb`](notebooks/01-baseline-nllb.ipynb) | Baseline NLLB-200 zero-shot (chrF++ / BLEU, FR→Éwé et Éwé→FR) |
| [`02-finetune-lora.ipynb`](notebooks/02-finetune-lora.ipynb) | Fine-tuning LoRA de NLLB-200 sur le corpus |

Les notebooks chargent les données **directement depuis ce dépôt** — aucun
téléchargement manuel. Exécution sur GPU T4 gratuit (~10-20 min pour le
fine-tuning).

### 2. Chargement du corpus

```python
import pandas as pd

train = pd.read_csv("data/processed/v0.2/train.tsv", sep="\t")
# colonnes : livre, chapitre, verset, fr, ewe, ratio, flag
```

## Structure

| Dossier | Rôle |
|---|---|
| `data/processed/v0.2/` | Corpus actif (train / dev / test + candidates à vérifier) |
| `data/grilles/` | 10 grilles de collecte (1 050 phrases FR) pour la traduction manuelle |
| `data/licenses/` | Matrice et décisions de licence par source |
| `src/clean/` | Pipeline de nettoyage : normalisation, extraction, alignement |
| `src/train/`, `src/evaluate/` | Entraînement et évaluation (à venir) |
| `notebooks/` | Notebooks Colab (baseline + fine-tuning) |
| `docs/` | Étude, plan, guide pratique, revue des ressources |

## Licence

Corpus publié sous **CC0-1.0** (sources domaine public, justificatifs dans
`data/licenses/`). Code sous licence MIT.
