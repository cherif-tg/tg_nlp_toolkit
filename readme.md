# Kabiyè-Éwé NLP Toolkit

Toolkit NLP open-source pour les langues togolaises : traduction automatique
**français ↔ éwé** (objectif principal), extension **kabiyè** prévue, ASR
conditionnel en phase finale.

## Modèle

Traducteur FR ↔ ÉWÉ fine-tuné, publié sur HuggingFace.
**Modèle recommandé (v2, bidirectionnel)** :
[`cheriftenga/nllb-200-distilled-600M-ewe-lora-v2`](https://huggingface.co/cheriftenga/nllb-200-distilled-600M-ewe-lora-v2)
V1 (unidirectionnelle, historique) :
[`cheriftenga/nllb-200-distilled-600M-ewe-lora`](https://huggingface.co/cheriftenga/nllb-200-distilled-600M-ewe-lora)
(NLLB-200-distilled-600M adapté par LoRA sur le corpus du projet).

### Scores officiels (test de référence vérifié, 241 paires)

| Direction | Baseline (zero-shot) | LoRA v1 | LoRA v2 |
|---|---|---|---|
| FR → ÉWÉ | chrF++ 37,22 — BLEU 11,17 | chrF++ 47,39 — BLEU 22,20 | **chrF++ 47,95 — BLEU 22,42** |
| ÉWÉ → FR | chrF++ 38,14 — BLEU 14,92 | chrF++ 37,52 — BLEU 15,15 | **chrF++ 52,24 — BLEU 31,83** |

La **v2** (entraînement bidirectionnel) corrige le sens ÉWÉ → FR :
**+14,72 chrF++** par rapport à la v1. Les deux directions sont désormais
au même niveau (~48 et ~52 chrF++).

**Benchmark Google Translate** (241 paires) : la v2 bat Google dans les
deux sens — FR→ÉWÉ 47,95 vs 38,62 (+9,33) ; ÉWÉ→FR 52,24 vs 49,86 (+2,38).
Voir [benchmark](docs/13-benchmark-google-translate.md).

### Sur le split test auto-aligné (6 564 paires, pour comparaison)

| Direction | Baseline (zero-shot) | Fine-tune LoRA |
|---|---|---|
| FR → ÉWÉ | chrF++ 34,96 — BLEU 11,38 | chrF++ 41,83 — BLEU 18,71 |
| ÉWÉ → FR | chrF++ 33,76 — BLEU 13,53 | chrF++ 33,35 — BLEU 13,69 |

Détails et exemples commentés : [baseline](docs/10-resultats-baseline.md),
[fine-tune v1](docs/11-resultats-finetune-lora.md) et
[fine-tune v2](docs/12-resultats-finetune-v2.md). Référence vérifiée :
[rapport](data/processed/v0.3/rapport-verification-reference.md).

## Corpus

Corpus parallèle **FR ↔ ÉWÉ v0.3** : **65 640 paires** (train 52 512 /
dev 6 564 / test 6 564), assemblées depuis :

- **Bible éwé 1913 (BFBS) + Bible Segond 1910** — alignement verset par
  verset, domaine public (~16 000 paires)
- **OPUS NLLB ee-fr v1** — corpus miné, filtré par un pipeline de qualité
  (éwé-ness + liste noire), licence ODC-By (~49 600 paires)

**Statut** : qualité documentée honnêtement (≈66 % biblique, ≈72 % NLLB) —
voir la [datasheet v0.3](data/processed/v0.3/DATASHEET.md).

**Dataset public sur HuggingFace** :
<https://huggingface.co/datasets/cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3>
(inclut le split `reference` : 241 paires vérifiées par double validation
humaine, 97 % de concordance entre vérificateurs).

## Utilisation

### 1. Démo interactive (Gradio)

```bash
pip install gradio transformers peft torch sentencepiece httpx
python demo/app.py                  # mode local (charge le modèle)
API_URL=http://127.0.0.1:8000 python demo/app.py   # mode API (léger)
```

Une démo publique est disponible sur HuggingFace Spaces :
<https://huggingface.co/spaces/cheriftenga/nllb-ewe-demo>

### 2. API REST (FastAPI)

```bash
pip install fastapi "uvicorn[standard]" httpx transformers peft torch sentencepiece
uvicorn src.api.main:app --reload --port 8000
```

- Documentation interactive : <http://127.0.0.1:8000/docs>
- `POST /translate` : `{"text": "...", "src": "fr", "tgt": "ewe"}`

### 3. CLI batch (campagnes, questionnaires)

```bash
python -m src.cli.translate --input messages.csv --src fr --tgt ewe --output messages_ewe.csv
# option --api http://127.0.0.1:8000 pour passer par l'API
```

### 4. Entraînement (Google Colab, GPU T4 gratuit)

| Notebook | Contenu |
|---|---|
| [`01-baseline-nllb.ipynb`](notebooks/01-baseline-nllb.ipynb) | Baseline NLLB-200 zero-shot (chrF++ / BLEU, FR→ÉWÉ et ÉWÉ→FR) |
| [`02-finetune-lora.ipynb`](notebooks/02-finetune-lora.ipynb) | Fine-tuning LoRA de NLLB-200 sur le corpus v0.3 |

Les notebooks chargent les données directement depuis ce dépôt.

### 5. Tests

```bash
python tests/test_api.py        # API REST
python tests/test_cli.py        # CLI batch
python tests/test_demo_api.py   # démo (mode API)
```

## Structure

| Dossier | Rôle |
|---|---|
| `data/processed/v0.3/` | Corpus actif (train / dev / test + datasheet) |
| `data/grilles/` | 10 grilles de collecte (1 050 phrases FR) pour la traduction manuelle |
| `data/licenses/` | Matrice et décisions de licence par source |
| `src/api/` | API REST FastAPI (endpoint /translate) |
| `src/cli/` | CLI de traduction batch |
| `src/clean/` | Pipeline de nettoyage : normalisation, extraction, alignement |
| `demo/` | Démo Gradio (modes local / API) |
| `spaces/` | Fichiers de déploiement HuggingFace Spaces |
| `notebooks/` | Notebooks Colab (baseline + fine-tuning) |
| `docs/` | Étude, guide d'utilisation, revue des ressources, résultats |
| `tests/` | Tests automatisés (API, CLI, démo) |

## Licence

- **Corpus** : CC0-1.0 (sources domaine public) + ODC-By (OPUS NLLB,
  attribution requise) — justificatifs dans `data/licenses/`
- **Modèle** : CC-BY-NC-SA-4.0 (héritée de NLLB, Meta AI — usage non
  commercial)
- **Code** : MIT
