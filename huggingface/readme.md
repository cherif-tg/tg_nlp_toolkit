---
license: cc0-1.0
language:
- fr
- ee
pretty_name: Corpus parallèle français-éwé v0.3 (Bible 1913 + NLLB filtré)
tags:
- translation
- machine-translation
- low-resource
- ewe
- french
- africa
task_categories:
- translation
language_details:
- name: Français
  code: fr
- name: Éwé (Ewe)
  code: ee
configs:
- config_name: default
  data_files:
  - split: train
    path: train.tsv
  - split: dev
    path: dev.tsv
  - split: test
    path: test.tsv
---

# Corpus parallèle français ↔ éwé — v0.3 (exploratoire)

Corpus de traduction **français ↔ éwé (ewe)** issu de deux composantes :

| Composante | Langues | Année | Licence |
|---|---|---|---|
| Bible éwé (BFBS) ↔ Segond 1910 | éwé / français | 1913 / 1910 | Domaine public → CC0-1.0 |
| NLLB `fr-ee` filtré (OPUS / allenai) | éwé / français | 2023 | **ODC-By** (attribution) |

## ⚠️ Statut honnête

**v0.3 exploratoire — non vérifié intégralement.** Qualité mesurée par
échantillons vérifiés par un **locuteur natif éwé** :

- Bible : **~66 %** (100 paires vérifiées)
- NLLB : **~72 %** estimé (100 paires vérifiées sur la version précédente, filtre v3 renforcé)

Le bruit restant est principalement de l'**alignement approximatif**
(corpus minés sur le web) — acceptable pour l'entraînement, pas pour
l'évaluation : un **test de référence vérifié à 100 %** est en préparation.

- ✅ **train / dev** : utilisables pour l'entraînement
- ⚠️ **test** : approximatif — utiliser le test de référence pour des scores fiables

## Statistiques (v0.3)

| Split | Paires | Bible | NLLB |
|---|---|---|---|
| train | 52 512 | 12 812 | 39 700 |
| dev | 6 564 | 1 601 | 4 963 |
| test | 6 564 | 1 601 | 4 963 |
| **Total** | **65 640** | 16 014 | 49 626 |

Colonnes : `source` (bible | nllb), `fr`, `ewe`.

## Licence

- Composante Bible : **domaine public** → publiée sous **CC0-1.0**
- Composante NLLB : **ODC-By** (Open Data Commons Attribution) — attribution
  requise : *NLLB dataset (allenai) via OPUS, ODC-By*
- Le tout est redistribué sous **CC0-1.0** avec attribution de la composante
  NLLB (l'attribution ODC-By est conservée dans cette fiche).

## Utilisation

```python
import pandas as pd

df = pd.read_csv("hf://datasets/cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3/train.tsv", sep="\t")
print(df.head())
```

Ou avec 🤗 `datasets` :

```python
from datasets import load_dataset

ds = load_dataset("cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3")
```

## Remarques sur les données

- **Registre** : biblique (Bible) + hétérogène web miné (NLLB : religieux,
  vie courante, actualités) — pas encore de domaine santé/administration ciblé
- **Orthographe** : éwé historique (1913) et éwé moderne (NLLB) mélangés —
  chaque paire garde la variante de sa source
- **Lexique Riebstein** (8 574 entrées FR→ÉWÉ, domaine public) : composant
  séparé dans le dépôt GitHub
- **Pipeline** : https://github.com/cherif-tg/tg_nlp_toolkit
  (`src/clean/` + `scripts/filter_nllb.py` + `scripts/assemble_v03.py`)

## Prochaines étapes

1. Test de référence vérifié (300 paires, 2+ locuteurs) → évaluation fiable
2. Fine-tuning NLLB-200 (LoRA) → scores de référence
3. Traduction manuelle des grilles (10 thèmes santé/administration)
