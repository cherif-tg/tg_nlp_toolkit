# Kabiyè-Éwé NLP Toolkit 🇹🇬

**Toolkit NLP open-source pour les langues togolaises** : traduction automatique
**français ↔ éwé** (objectif n°1), extension **kabiyè** en option, et **ASR
conditionnel** en phase finale.

> 🎯 **Mission** : donner aux langues togolaises (éwé, kabiyè et autres) les
> mêmes outils numériques que les grandes langues — traduction, reconnaissance
> vocale — en partant de zéro, avec des données libres et vérifiées par des
> locuteurs natifs.

---

## 📊 État d'avancement

| Phase | Contenu | Statut |
|---|---|---|
| **P0** | Cadrage : étude, plan, licences, grilles de collecte (1 050 phrases FR, 10 thèmes) | ✅ Terminé |
| **P1** | Corpus v0.2 FR↔Éwé : 16 050 paires « ok » (train 12 844 / dev 1 603 / test 1 603) | ✅ Terminé (exploratoire) |
| **P2** | Notebooks d'entraînement : baseline NLLB zero-shot + fine-tuning LoRA | ✅ Prêts (Colab) |
| **P2** | Entraînement du modèle de référence (NLLB-200-distilled-600M) | 🔜 En attente (Colab) |
| **P3** | Démo Gradio + API REST + CLI batch | ⏳ À venir |
| **P4** | ASR conditionnel (Whisper fine-tune) + extension kabiyè | ⏳ À venir |
| **—** | Publication HuggingFace (corpus + modèles) | 📦 Prête (privé → public) |

---

## 🧪 Le corpus v0.2

Corpus parallèle **français ↔ éwé** aligné automatiquement depuis deux sources
**domaine public** :

- **Bible éwé 1913** (BFBS, archive.org) — OCR complet normalisé (51 422
  homoglyphes cyrilliques corrigés, 66 livres localisés, 25 581 versets)
- **Bible Segond 1910** (édition domaine public) — 31 170 versets

**Pipeline** : collecte → normalisation → extraction → alignement DP (23 549
paires, 100 % numéros identiques) → nettoyage calibré sur vérification humaine
→ splits 80/10/10 (seed 42).

**Qualité mesurée** (échantillon de 100 paires vérifié par un locuteur natif) :
~66 % de paires correctes sur le noyau. Statut **honnêtement documenté** dans
[`data/processed/v0.2/DATASHEET.md`](data/processed/v0.2/DATASHEET.md).

> ⚠️ Le corpus est un **outil d'entraînement** (le bruit est toléré). Le test
> set devra être vérifié intégralement avant de publier des scores de
> référence — c'est la prochaine étape de validation.

---

## 🚀 Démarrage rapide (entraînement sur Colab)

Les notebooks chargent les données **directement depuis ce repo GitHub** — aucun
téléchargement manuel.

1. **Baseline zero-shot** : [`notebooks/01-baseline-nllb.ipynb`](notebooks/01-baseline-nllb.ipynb)
   — mesure la qualité de NLLB-200 sans entraînement (chrF++ / BLEU, FR→Éwé et Éwé→FR)
2. **Fine-tuning LoRA** : [`notebooks/02-finetune-lora.ipynb`](notebooks/02-finetune-lora.ipynb)
   — adapte NLLB à notre corpus (~10-20 min sur un T4 gratuit)

Instructions détaillées : voir [`docs/05-guide-utilisation-pratique.md`](docs/05-guide-utilisation-pratique.md).

---

## 📁 Structure du dépôt

| Dossier | Rôle |
|---|---|
| `docs/` | Cahier des charges, document d'étude v2.0, plan détaillé, guide pratique, revue des ressources |
| `data/raw/` | Sources brutes (jamais modifiées) |
| `data/processed/v0.2/` | **Corpus actif** : train / dev / test + candidates à vérifier + datasheet |
| `data/grilles/` | 10 grilles de collecte (1 050 phrases FR) pour la traduction manuelle |
| `data/licenses/` | Matrice des licences + décision écrite par source |
| `src/collect/` | Scripts de collecte |
| `src/clean/` | Normalisation, extraction, alignement, nettoyage (pipeline complet) |
| `src/augment/` | Back-translation + filtrage (à venir) |
| `src/train/` | Fine-tuning NLLB / Whisper (à venir) |
| `src/evaluate/` | Évaluation chrF++ / COMET / BLEU / WER (à venir) |
| `notebooks/` | Notebooks Colab (baseline + LoRA) |
| `huggingface/` | **Dossier de publication HuggingFace** (dataset card + données + licences) |
| `demo/` | Application Gradio (P3) |
| `models/` | Artefacts locaux (gitignorés) |
| `tests/` | Tests unitaires |
| `scripts/` | Scripts one-shot : `build_notebooks.py`, `push_to_hub.py`… |

---

## 📦 Publication HuggingFace

Le corpus est prêt à publier sous **CC0-1.0** (sources domaine public →
dédicace au domaine public). Dossier : [`huggingface/`](huggingface/).

```bash
# 1. Installer le client HF
pip install huggingface_hub

# 2. Publier (privé par défaut — recommandé tant que le test n'est pas vérifié)
python scripts/push_to_hub.py

# 3. Après vérification du test set : passer le dataset en public sur le site
```

> 🔒 **Recommandation** : publier d'abord en **privé**, vérifier le test set,
> puis passer en public. Les modèles fine-tunés seront publiés séparément
> (repo `cheriftenga`).

---

## 🧾 Licences & éthique

- **Règle d'or** : une source = une décision écrite de licence avant intégration
  (voir [`data/licenses/`](data/licenses/))
- **Corpus publié** : sources domaine public uniquement
- **JW300 (Témoins de Jéhovah)** : **entraînement uniquement, jamais publié** —
  licence restrictive
- **Consentement** : formulaires pour les traducteurs avant toute collecte humaine

---

## 🤝 Contribuer

Ce projet vit grâce à la communauté. Besoins prioritaires :

1. **Locuteurs natifs éwé** : vérification du test set, traduction des grilles
2. **Locuteurs kabiyè** : même travail pour la 2ᵉ langue
3. **ML engineers** : entraînement, évaluation, déploiement

Comment procéder : ouvrir une issue ou contacter le mainteneur (voir GitHub
profile). Les instructions de vérification sont dans
[`docs/05-guide-utilisation-pratique.md`](docs/05-guide-utilisation-pratique.md).

---

## 👥 Équipe

- **Cherif** — futur AI Engineer (École Polytechnique de Lomé), locuteur éwé,
  concepteur du projet
- **Sukuna** — agent de codage (pipeline de données, automatisation)

**HuggingFace** : [cheriftenga](https://huggingface.co/cheriftenga)

---

*Projet de démonstration de la faisabilité du NLP en langues togolaises —
données libres, méthodes reproductibles, résultats honnêtes.*
