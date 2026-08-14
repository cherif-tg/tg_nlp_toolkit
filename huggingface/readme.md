---
license: cc0-1.0
language:
- fr
- ee
pretty_name: Corpus parallèle français-éwé v0.2 (Bible éwé 1913 ↔ Segond 1910)
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

# Corpus parallèle français ↔ éwé — v0.2 (exploratoire)

Corpus de traduction **français ↔ éwé (ewe)** aligné automatiquement depuis
deux sources en **domaine public** :

| Source | Langue | Année | Statut |
|---|---|---|---|
| Bible éwé (BFBS) | éwé | 1913 | Domaine public (archive.org, OCR) |
| Bible Segond 1910 (UBS/PD) | français | 1910 | Domaine public |

## ⚠️ Statut honnête

**v0.2 exploratoire — non vérifié intégralement.** Un échantillon de 100 paires
a été vérifié par un **locuteur natif éwé** : qualité estimée **~66 %** sur le
noyau (51 ok / 31 corriger / 18 rejeter). Les erreurs restantes sont
principalement des fausses correspondances (verset mal aligné) et des résidus
d'OCR.

- ✅ **train / dev** : utilisables pour l'entraînement (le bruit est toléré par les modèles)
- ⚠️ **test** : à vérifier par un locuteur avant de publier des scores fiables

## Statistiques (v0.2)

| Split | Paires |
|---|---|
| train | 12 844 |
| dev | 1 603 |
| test | 1 603 |
| **Total « ok »** | **16 050** |
| Candidates « à vérifier » (non publiées ici) | 7 499 |

Colonnes : `livre`, `chapitre`, `verset`, `fr`, `ewe`, `ratio`, `flag`.

## Licence

Les deux sources sont en **domaine public**. Ce corpus est publié sous
**CC0-1.0** (dédicace au domaine public) : utilisation libre, y compris
commerciale, sans attribution requise.

Voir `data/licenses/` du dépôt GitHub pour les justificatifs.

## Utilisation

```python
import pandas as pd

df = pd.read_csv("hf://datasets/cheriftenga/tg-nlp-toolkit-fr-ewe-v0.2/train.tsv", sep="\t")
print(df.head())
```

Ou avec 🤗 `datasets` :

```python
from datasets import load_dataset

ds = load_dataset("cheriftenga/tg-nlp-toolkit-fr-ewe-v0.2")
```

## Remarques sur les données

- **Registre** : biblique uniquement (pas encore de domaine santé/administration)
- **Orthographe** : éwé de 1913, avec quelques diacritiques manquants
- **Noms de livres** : codes standard (`GEN`, `MAT`, `REV`…)
- **Pipeline** : https://github.com/cherif-tg/tg_nlp_toolkit (dossier `src/clean/`)

## Prochaines étapes

1. Vérification du test set par des locuteurs natifs → v1.0
2. Fine-tuning NLLB-200 (LoRA) → scores de référence
3. Traduction manuelle des grilles (10 thèmes santé/administration) → extension de domaine
