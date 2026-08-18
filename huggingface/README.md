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
- togo
task_categories:
- translation
configs:
- config_name: default
  data_files:
  - split: train
    path: train.tsv
  - split: dev
    path: dev.tsv
  - split: test
    path: test.tsv
  - split: reference
    path: test-reference-final.tsv
---

# Corpus parallèle français - éwé v0.3

Corpus de traduction **français - éwé (ewe)** pour le machine translation
en contexte de faible ressource, construit à partir de deux composantes :

| Composante | Langues | Année | Licence |
|---|---|---|---|
| Bible éwé (BFBS) - Segond 1910 | éwé / français | 1913 / 1910 | Domaine public - CC0-1.0 |
| NLLB `fr-ee` filtré (OPUS / allenai) | éwé / français | 2023 | **ODC-By** (attribution) |

## Test de référence vérifié (split `reference`)

Le split **`reference`** contient **241 paires vérifiées à 100 %** par
**double validation indépendante** (2 locuteurs natifs éwé, 97 % de
concordance entre vérificateurs, arbitrage final) :

- 124 paires Bible + 117 paires NLLB
- Verdicts par paire : ok / corriger / à rejeter ; seules les paires
  validées par les deux vérificateurs sont conservées
- Archive complète des vérifications : `test-reference-verifs.csv`
  dans le [repo GitHub](https://github.com/cherif-tg/tg_nlp_toolkit)
  (`data/processed/v0.3/`), avec le rapport détaillé

C'est la référence recommandée pour **évaluer** des systèmes FR-éwé :
le split `test` (auto-aligné) est utile pour l'entraînement et la
comparaison interne, mais la référence vérifiée est la seule base de
scores fiables.

## Statut honnête

**Corpus d'entraînement exploratoire** - qualité mesurée par échantillons
vérifiés par locuteur natif :

- Bible : ~66 % de paires correctes (100 paires vérifiées)
- NLLB filtré v3 : ~72 % (100 paires vérifiées, langues étrangères retirées)

Le bruit restant est principalement de l'**alignement approximatif**
(corpus miné sur le web) - documenté en détail dans le datasheet.
Acceptable pour l'entraînement ; d'où le test de référence vérifié
pour l'évaluation.

## Statistiques (v0.3)

| Split | Paires | Bible | NLLB |
|---|---|---|---|
| train | 52 512 | 12 812 | 39 700 |
| dev | 6 564 | 1 601 | 4 963 |
| test | 6 564 | 1 601 | 4 963 |
| reference (vérifiée) | **241** | 124 | 117 |
| **Total** | 65 640 | 16 014 | 49 626 |

Colonnes : `id`, `source` (bible | nllb), `fr`, `ewe` pour le split
`reference` ; `source`, `fr`, `ewe` pour les autres.

## Résultats de modèles entraînés sur ce corpus

### Scores officiels (sur le split `reference` vérifié, 241 paires)

| Direction | Modèle | chrF++ | BLEU |
|---|---|---|---|
| FR -> éwé | NLLB baseline | 37,22 | 11,17 |
| FR -> éwé | + LoRA fine-tune | **47,39** | **22,20** |
| éwé -> FR | NLLB baseline | 38,14 | 14,92 |
| éwé -> FR | + LoRA fine-tune | 37,52 | 15,15 |

Gain FR -> éwé : **+10,17 chrF++** et **+11,03 BLEU** par rapport au
zero-shot. Le sens éwé -> FR ne progresse pas (modèle v1 unidirectionnel) :
prévu par le fine-tuning v2.

### Sur le split `test` auto-aligné (6 564 paires, pour comparaison)

| Direction | Modèle | chrF++ | BLEU |
|---|---|---|---|
| FR -> éwé | NLLB baseline | 34,96 | 11,38 |
| FR -> éwé | + LoRA fine-tune | 41,83 | 18,71 |
| éwé -> FR | NLLB baseline | 33,76 | 13,53 |
| éwé -> FR | + LoRA fine-tune | 33,35 | 13,69 |

Modèle publié : [cheriftenga/nllb-200-distilled-600M-ewe-lora](https://huggingface.co/cheriftenga/nllb-200-distilled-600M-ewe-lora)

## Licence

- Composante Bible : **domaine public** - publiée sous **CC0-1.0**
- Composante NLLB : **ODC-By** (Open Data Commons Attribution) - attribution
  requise : *NLLB dataset (allenai) via OPUS, ODC-By*
- L'ensemble est redistribué sous **CC0-1.0** avec attribution de la
  composante NLLB (l'attribution ODC-By est conservée dans cette fiche).
- Le split `reference` (vérifications humaines) : **CC0-1.0**.

## Utilisation

```python
from datasets import load_dataset

ds = load_dataset("cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3")
print(ds["reference"][0])
```

Ou lecture directe des TSV :

```python
import pandas as pd

df = pd.read_csv("hf://datasets/cheriftenga/tg-nlp-toolkit-fr-ewe-v0.3/train.tsv", sep="\t")
```

## Remarques sur les données

- **Registre** : biblique (Bible) + hétérogène web miné (NLLB : religieux,
  vie courante, actualités)
- **Orthographe** : éwé historique (1913) et éwé moderne (NLLB) mélangés -
  chaque paire garde la variante de sa source (politique de variantes :
  une source = sa variante documentée)
- **Variantes** : le vérificateur principal du split `reference` est
  locuteur de l'éwé côtier de Lomé
- **Lexique Riebstein** (8 574 entrées FR-éwé, domaine public) : composant
  séparé dans le dépôt GitHub
- **Pipeline complet** : https://github.com/cherif-tg/tg_nlp_toolkit
  (`src/clean/` + `scripts/filter_nllb.py` + `scripts/assemble_v03.py`)

## Auteur

TENGA Cherif Abdel Azize - projet de fin d'études (École Polytechnique
de Lomé, Togo). Corpus construit avec documentation honnête de la
qualité : chaque taux annoncé est mesuré sur échantillon vérifié.

## Prochaines étapes

1. Scores officiels des modèles sur le split `reference` (241 paires)
2. Fine-tuning v2 bidirectionnel (éwé -> FR en cours d'amélioration)
3. Extension : grilles thématiques santé/administration (10 thèmes,
   traduction manuelle en cours) + composante audio (ASR)
